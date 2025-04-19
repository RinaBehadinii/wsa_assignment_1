# Fullstack Web Store Application

This repository contains both the frontend and backend code for an e-commerce platform. The backend is built using Django and Django REST Framework, while the frontend is built using ReactJS.

## Backend Setup (Django)

The backend is built using Django, and the project is structured to use Django REST Framework to expose APIs for the frontend to interact with.

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/RinaBehadinii/wsa_assignment_1.git
    cd wsa_assignment_1
    ```

2. Create a virtual environment:

    ```bash
    python -m venv venv
    ```

3. Activate the virtual environment:
    - **Windows**: `venv\Scripts\activate`
    - **Linux/macOS**: `source venv/bin/activate`

4. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Apply the database migrations:

    ```bash
    python manage.py migrate
    ```

6. Create a superuser (admin):

    ```bash
    python manage.py createsuperuser
    ```

7. Run the server:

    ```bash
    python manage.py runserver
    ```

Your backend API should now be running at `http://127.0.0.1:8000/`.

### API Endpoints

- **Authentication**
  - `POST /api/token/`: Obtain access and refresh tokens.
  - `POST /api/token/refresh/`: Refresh an expired access token.

- **Users**
  - `GET /users/`: List all users (requires admin permissions).
  - `POST /register/`: Register a new user.

- **Products**
  - `GET /products/`: List all products.
  - `GET /products/search/`: Search products by category, brand, price, etc.
  - `GET /products/{id}/quantity/`: Get stock information for a specific product.
  - `POST /products/`: Create a new product (requires admin permissions).
  - `PUT /products/{id}/`: Update a product (requires admin permissions).
  - `DELETE /products/{id}/`: Delete a product (requires admin permissions).

- **Orders**
  - `GET /orders/`: List all orders (only for admin/advanced users, simple users can see their own).
  - `POST /orders/`: Place a new order.
  - `PATCH /orders/{id}/`: Update the status of an order (requires admin permission).

- **Reports**
  - `GET /reports/daily_earnings/`: Get daily earnings (requires admin/advanced user).
  - `GET /reports/top_selling_products/`: Get the top-selling products (requires admin/advanced user).

## Frontend Setup (React)

The frontend is built using React and communicates with the backend API.

### Prerequisites

- Node.js (LTS version)
- npm or yarn

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/RinaBehadinii/wsa_assignment_1.git
    cd wsa_assignment_1
    ```

2. Install the dependencies:

    ```bash
    npm install
    ```

3. Start the development server:

    ```bash
    npm start
    ```

Your frontend should now be running at `http://localhost:3000/`.

## Technologies Used

- **Backend**: Django, Django REST Framework
- **Frontend**: ReactJS
- **Authentication**: JWT (JSON Web Tokens)
- **Database**: SQLite
