from django.contrib.auth.models import User, Group
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from products.serializer import (
    CategorySerializer, BrandSerializer, SizeSerializer, ColorSerializer, GenderSerializer,
    ProductSerializer, UserSerializer, OrderSerializer,
    DiscountSerializer, ReportSerializer, CustomTokenObtainPairSerializer
)
from .models import Category, Brand, Size, Color, Gender, Product, Order, OrderDetail, Discount, Report
from .permissions import IsAdmin, IsAdvancedUser


class RegisterView(APIView):
    permission_classes = []  # Allow anyone to access this endpoint

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if User.objects.filter(username=username).exists():
            raise ValidationError({'username': 'Username is already taken.'})
        if User.objects.filter(email=email).exists():
            raise ValidationError({'email': 'Email is already registered.'})

        user = User.objects.create_user(username=username, email=email, password=password)

        try:
            simple_user_group, created = Group.objects.get_or_create(name="Simple User")
            user.groups.add(simple_user_group)  # Add the user to the "Simple User" group
        except Exception as e:
            return Response({'error': f'Could not assign default group: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'User registered successfully!'}, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated]


class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    permission_classes = [IsAuthenticated]


class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [IsAuthenticated]


class GenderViewSet(viewsets.ModelViewSet):
    queryset = Gender.objects.all()
    serializer_class = GenderSerializer
    permission_classes = [IsAuthenticated]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdmin(), IsAdvancedUser()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def search(self, request):
        queryset = Product.objects.all()
        category = request.query_params.get('category')
        gender = request.query_params.get('gender')
        brand = request.query_params.get('brand')
        price_min = request.query_params.get('price_min')
        price_max = request.query_params.get('price_max')
        size = request.query_params.get('size')
        color = request.query_params.get('color')

        if category:
            queryset = queryset.filter(category__name__icontains=category)
        if gender:
            queryset = queryset.filter(gender__type__icontains=gender)
        if brand:
            queryset = queryset.filter(brand__name__icontains=brand)
        if price_min and price_max:
            queryset = queryset.filter(price__gte=price_min, price__lte=price_max)
        if size:
            queryset = queryset.filter(size__size__icontains=size)
        if color:
            queryset = queryset.filter(color__name__icontains=color)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def quantity(self, request, pk=None):
        product = get_object_or_404(Product, pk=pk)
        sold_quantity = OrderDetail.objects.filter(product=product).aggregate(total_sold=Sum('quantity'))[
                            'total_sold'] or 0
        current_quantity = product.quantity - sold_quantity
        return Response({
            "product_id": product.id,
            "name": product.name,
            "initial_quantity": product.quantity,
            "sold_quantity": sold_quantity,
            "current_quantity": current_quantity
        })


class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.data.get('user')
        if not user:
            raise ValidationError({"user": "This field is required."})

        try:
            user_obj = User.objects.get(id=user)
        except User.DoesNotExist:
            raise ValidationError({"user": "User does not exist."})

        serializer.save(user=user_obj)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update']:
            return [IsAdmin()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['get'])
    def groups(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        groups = user.groups.values_list('name', flat=True)
        return Response({'groups': list(groups)})


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    def get_permissions(self):
        if self.action in ['daily_earnings', 'top_selling_products']:
            return [IsAdmin(), IsAdvancedUser()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def daily_earnings(self, request):
        today = timezone.now().date()
        orders = Order.objects.filter(order_date__date=today)
        total_earnings = sum(
            detail.price_at_purchase * detail.quantity for order in orders for detail in order.order_details.all())
        return Response({"date": today, "total_earnings": total_earnings})

    @action(detail=False, methods=['get'])
    def top_selling_products(self, request):
        top_products = OrderDetail.objects.values('product__name').annotate(total_sold=Sum('quantity')).order_by(
            '-total_sold')[:10]
        return Response(top_products)
