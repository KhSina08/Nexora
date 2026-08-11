from django.shortcuts import render
from django.http import JsonResponse
from apps.products.models import ProductVariant
import json

def cart_detail(request):

    cart = request.session.get("cart", {})

    items = []
    total_price = 0

    for variant_id, quantity in cart.items():

        try:
            variant = ProductVariant.objects.get(id=variant_id)

            price = variant.price
            subtotal = price * quantity

            image = None
            img = variant.images.filter(is_primary=True).first() or variant.images.first()
            if img:
                image = img.image.url

            items.append({
                "id": variant.id,
                "name": variant.product.name,
                "price": price,
                "quantity": quantity,
                "subtotal": subtotal,
                "image": image,
                "sku": variant.sku
            })

            total_price += subtotal

        except ProductVariant.DoesNotExist:
            continue

    return render(request, "cart.html", {
        "items": items,
        "total": total_price
    })


def remove_from_cart(request, variant_id):

    cart = request.session.get("cart", {})

    if str(variant_id) in cart:
        del cart[str(variant_id)]

    request.session["cart"] = cart

    return JsonResponse({"success": True})



def add_to_cart(request):

    if request.method == "POST":

        data = json.loads(request.body)

        variant_id = str(data.get("variant_id"))
        quantity = int(data.get("quantity", 1))

        cart = request.session.get("cart", {})

        if variant_id in cart:
            cart[variant_id] += quantity
        else:
            cart[variant_id] = quantity

        request.session["cart"] = cart

        return JsonResponse({
            "success": True,
            "cart": cart
        })

    return JsonResponse({"error": "Invalid request"})




def update_cart(request):

    if request.method == "POST":

        data = json.loads(request.body)

        variant_id = str(data.get("variant_id"))
        action = data.get("action")

        cart = request.session.get("cart", {})

        if variant_id not in cart:
            return JsonResponse({"error": "Item not in cart"})

        # ✅ تغییر quantity
        if action == "increase":
            cart[variant_id] += 1

        elif action == "decrease":
            cart[variant_id] -= 1
            if cart[variant_id] <= 0:
                del cart[variant_id]

        request.session["cart"] = cart

        # ✅ محاسبه واقعی از دیتابیس
        items = []
        total = 0

        for vid, qty in cart.items():
            variant = ProductVariant.objects.get(id=vid)

            subtotal = variant.price * qty
            total += subtotal

            items.append({
                "variant_id": variant.id,
                "quantity": qty,
                "price": float(variant.price),
                "subtotal": float(subtotal)
            })

        return JsonResponse({
            "success": True,
            "items": items,
            "total": float(total)
        })

    return JsonResponse({"error": "Invalid request"})