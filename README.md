# E-commerce Django API

An E-commerce Django API that supports coupon codes and payment integration using Stripe and/or M-Pesa, with order management, stock tracking, and automated notifications.

## Features

- **User Authentication & Authorization:** Secure user registration, login, and role-based access control.
- **Product Management:** Create, update, retrieve, and delete products with filtering, pagination, and Markdown-supported descriptions.  
- **Order Processing:** Manage orders efficiently with stock tracking, automatic order completion on payment, and order history.
- **Coupon System:** Support for product-specific, optional discount coupons to enhance promotions.  
- **Payment Integration:** Seamless integration with Stripe and M-Pesa for secure transactions.  
- **Automated Notifications:** Email notifications for order confirmations, invoices (with PDF generation), and payment updates.  
- **Stock Management:** Automatic stock deduction upon order placement with validation and restoration on failure.  
- **Documentation:** Auto-generated API documentation using Swagger or DRF's built-in docs.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Django 3.x or later
- Django REST Framework
- Stripe

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Maksym-TopDev/Custom_E-Commerce_API_For_Payment.git
   cd ecommerce
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Create .env with the following variables:**
    ```
    SECRET_KEY=
    DJANGO_ALLOWED_HOSTS=<separated by space>
    DEBUG=
    STRIPE_SECRET_KEY=
    STRIPE_WEBHOOK_SECRET=
    MPESA_CONSUMER_KEY=
    MPESA_CONSUMER_SECRET=
    MPESA_SHORTCODE=
    MPESA_PASSKEY=
    MPESA_ENV=
    MPESA_CALLBACK_URL=
    ```

4. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up Redis:**
   Ensure Redis is installed and running on your machine. You can download and install Redis from [here](https://redis.io/download).

6. **Configure the Django settings:**
   Update your `settings.py` to connect to your Redis instance.

7. **Run the migrations:**
   ```bash
   python manage.py migrate
   ```

8. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

9. **Start the Django development server:**
   ```bash
   python manage.py runserver
   ```

## Usage  

Before testing the API locally, ensure you have created a superuser (Admin) using ```python manage.py createsuperuser``` and register a user (Customer) using ```http://localhost:8000/register```

### Admin Access  
- The Django Admin Panel is available at: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)  
- Admin users can:  
  - Manage products, categories, and coupons  
  - View and track stock logs  
  - Monitor and process orders  

### Customer Access  
- Regular users can:  
  - Browse all available products at: [http://127.0.0.1:8000/api/products/](http://127.0.0.1:8000/api/products/)  
  - Place orders at: [http://127.0.0.1:8000/api/orders/](http://127.0.0.1:8000/api/orders/)  
  - Add multiple products to their cart and check out  

For further API interactions, refer to the auto-generated documentation at:  
[http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/) (Swagger UI)
