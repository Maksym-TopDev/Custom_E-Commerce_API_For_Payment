from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from accounts import views
from django.contrib.auth import views as auth_views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# from drf-yasg documentation
schema_view = get_schema_view(
   openapi.Info(
      title="A Custom E-Commerce API",
      default_version='v1',
      description="A scalable and secure API for customizable e-commerce solutions tailored for small businesses. \nSupports for coupon codes and payment integration (Stripe) and m-pesa. \nSome of the features include real-time inventory updates, webhook-driven payment status tracking, and optimized API performance for seamless order management.",
      terms_of_service="https://www.example.com/terms/",
      contact=openapi.Contact(email=""),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("register/", views.register, name="register" ),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),


    # Protected endpoints for logged in users
    path('admin/', admin.site.urls),
    path("", include("users.urls")),
    path("", include("products.urls")),
    path("", include("orders.urls")),
    path("", include("payments.urls")),

    # token generation url
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Documentaing using drf-yasg
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
