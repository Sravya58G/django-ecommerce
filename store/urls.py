from django.contrib import admin
from django.urls import path
from shop import views
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("product/<int:pk>/", views.detail, name="detail"),
    path("add/<int:pk>/", views.add, name="add"),
    path("cart/", views.cart, name="cart"),
    path("remove/<int:pk>/", views.remove, name="remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.orders, name="orders"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
