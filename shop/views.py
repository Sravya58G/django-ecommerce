from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from .models import Product, Order

def home(request):
    return render(request, "home.html", {"products": Product.objects.all()})

def detail(request, pk):
    return render(request, "detail.html", {"p": get_object_or_404(Product, pk=pk)})

@require_POST
def add(request, pk):
    p = get_object_or_404(Product, pk=pk)
    cart = request.session.get("cart", {})
    key = str(pk)
    if p.stock > cart.get(key, 0):
        cart[key] = cart.get(key, 0) + 1
        request.session["cart"] = cart
    else:
        messages.error(request, "No more stock available.")
    return redirect("cart")

def cart(request):
    data, total = [], Decimal("0")
    basket = request.session.get("cart", {})
    for key, qty in basket.items():
        p = Product.objects.filter(pk=key).first()
        if p and qty > 0:
            subtotal = p.price * qty
            data.append({"p": p, "qty": qty, "subtotal": subtotal})
            total += subtotal
    return render(request, "cart.html", {"data": data, "total": total})

@require_POST
def remove(request, pk):
    basket = request.session.get("cart", {})
    basket.pop(str(pk), None)
    request.session["cart"] = basket
    return redirect("cart")

def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("home")
    return render(request, "form.html", {"form": form, "heading": "Register"})

def login_view(request):
    from django.contrib.auth.forms import AuthenticationForm
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("home")
    return render(request, "form.html", {"form": form, "heading": "Login"})

def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("home")

@login_required
def checkout(request):
    basket = request.session.get("cart", {})
    products, total = [], Decimal("0")
    for key, qty in basket.items():
        p = Product.objects.filter(pk=key).first()
        if p and qty > 0:
            products.append((p, qty))
            total += p.price * qty
    if not products:
        messages.info(request, "Your cart is empty.")
        return redirect("home")
    if request.method == "POST":
        if any(p.stock < qty for p, qty in products):
            messages.error(request, "Insufficient stock. Please review your cart.")
            return redirect("cart")
        descriptions = []
        for p, qty in products:
            descriptions.append(f"{p.name} x {qty}")
            p.stock -= qty
            p.save()
        Order.objects.create(user=request.user, items=", ".join(descriptions), total=total)
        request.session["cart"] = {}
        messages.success(request, "Order placed successfully!")
        return redirect("orders")
    return render(request, "checkout.html", {"products": products, "total": total})

@login_required
def orders(request):
    return render(request, "orders.html", {"orders": Order.objects.filter(user=request.user).order_by("-created")})
