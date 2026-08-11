from django.urls import path
from . import views


app_name = "orders"

urlpatterns = [
    path(
        "checkout/",
        views.checkout,
        name="checkout"
    ),

    path(
        "success/<int:order_id>/",
        views.success,
        name="success"
    ),
    
    
    path("my-orders/", views.order_list, name="order_list"),
    path("<int:order_id>/", views.order_detail, name="order_detail"),
    
    path("payment/<int:order_id>/", views.payment, name="payment"),

    path("payment/verify/", views.payment_verify, name="payment_verify"),
]