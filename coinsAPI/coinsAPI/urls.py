"""
URL configuration for btcAPI project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from coins import views

urlpatterns = [
    path("admin/", admin.site.urls),

    #### API ####
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("unlog/", views.register, name="unlog"),

    path("new_payment/", views.new_payment_view, name="new_payment"),

    path("get_coins_rate/", views.coins_rate, name="coins_rate"),
    path("get_payment_requests/", views.get_payment_requests, name="get_payment_requests"),
    path("get_active_payment_requests/", views.get_active_payment_requests, name="get_active_payment_requests"),
    path("get_payment_request_by_id_public/", views.get_payment_request_by_id_public, name="get_payment_request_by_id_public"),
    path("get_payment_request_by_address_public/", views.get_payment_request_by_address_public, name="get_payment_request_by_address_public"),
    path("get_available_funds/", views.available_funds, name="get_available_funds"),

    path("withdraw/", views.withdraw_funds, name="withdraw"),

    path("buy_plan/", views.buy_plan, name="buy_plan")
]
