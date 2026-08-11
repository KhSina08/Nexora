from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from apps.products.models import ProductVariant

from .models import Order, OrderItem


@login_required
def checkout(request):

    cart = request.session.get("cart", {})


    if not cart:
        messages.warning(
            request,
            "سبد خرید شما خالی است."
        )
        return redirect("cart:cart_page")


    items = []
    total_price = 0


    variants = ProductVariant.objects.filter(
        id__in=cart.keys(),
        is_active=True
    )


    variants_map = {
        str(v.id): v
        for v in variants
    }


    # بررسی cart
    for variant_id, quantity in cart.items():

        variant = variants_map.get(
            str(variant_id)
        )


        if not variant:
            messages.error(
                request,
                "یکی از محصولات دیگر موجود نیست."
            )
            return redirect(
                "cart:cart_page"
            )


        if quantity <= 0:
            messages.error(
                request,
                "تعداد محصول نامعتبر است."
            )
            return redirect(
                "cart:cart_page"
            )


        subtotal = variant.price * quantity

        total_price += subtotal


        items.append({
            "variant": variant,
            "quantity": quantity,
            "subtotal": subtotal
        })


    if request.method == "POST":


        first_name = request.POST.get(
            "first_name",
            ""
        ).strip()


        last_name = request.POST.get(
            "last_name",
            ""
        ).strip()


        phone = request.POST.get(
            "phone",
            ""
        ).strip()


        address = request.POST.get(
            "address",
            ""
        ).strip()


        city = request.POST.get(
            "city",
            ""
        ).strip()


        postal_code = request.POST.get(
            "postal_code",
            ""
        ).strip()



        if not all([
            first_name,
            last_name,
            phone,
            address,
            city,
            postal_code
        ]):

            messages.error(
                request,
                "لطفاً همه اطلاعات را کامل کنید."
            )

            return redirect(
                "orders:checkout"
            )


        try:

            with transaction.atomic():


                # قفل موجودی
                locked_variants = (
                    ProductVariant.objects
                    .select_for_update()
                    .filter(
                        id__in=[
                            item["variant"].id
                            for item in items
                        ]
                    )
                )


                locked_map = {
                    v.id: v
                    for v in locked_variants
                }



                # بررسی موجودی
                for item in items:

                    variant = locked_map[
                        item["variant"].id
                    ]

                    quantity = item["quantity"]


                    if (
                        variant.manage_stock
                        and variant.stock < quantity
                    ):

                        messages.error(
                            request,
                            f"{variant} موجودی کافی ندارد."
                        )

                        return redirect(
                            "cart:cart_page"
                        )



                # ساخت Order
                order = Order.objects.create(

                    user=request.user,

                    first_name=first_name,

                    last_name=last_name,

                    phone=phone,

                    address=address,

                    city=city,

                    postal_code=postal_code,

                    total_price=total_price,

                    payment_status="unpaid"

                )



                order_items = []


                for item in items:


                    variant = locked_map[
                        item["variant"].id
                    ]


                    quantity = item["quantity"]



                    if variant.manage_stock:

                        variant.stock -= quantity

                        variant.save()



                    order_items.append(

                        OrderItem(
                            order=order,
                            variant=variant,
                            quantity=quantity,
                            price=variant.price
                        )

                    )



                OrderItem.objects.bulk_create(
                    order_items
                )



        except Exception as e:

            print(
                "CHECKOUT ERROR:",
                e
            )

            messages.error(
                request,
                "خطا در ثبت سفارش."
            )

            return redirect(
                "cart:cart_page"
            )



        # پاک کردن cart
        request.session["cart"] = {}

        request.session.modified = True



        return redirect(
            "orders:payment",
            order_id=order.id
        )



    return render(
        request,
        "checkout.html",
        {
            "items": items,
            "total": total_price
        }
    )



@login_required
def success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )


    return render(
        request,
        "orders/success.html",
        {
            "order": order
        }
    )



@login_required
def order_list(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by(
        "-created_at"
    )


    return render(
        request,
        "orders/order_list.html",
        {
            "orders": orders
        }
    )



@login_required
def order_detail(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )


    return render(
        request,
        "orders/order_detail.html",
        {
            "order": order
        }
    )
    
    
    
    
    
@login_required
def payment(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if order.payment_status != "unpaid":
        return redirect("orders:success", order_id=order.id)


    from .services.payment import create_payment

    payment_data = create_payment(order)

    return render(
        request,
        "orders/payment.html",
        {
            "order": order,
            "payment_url": payment_data["payment_url"],
        }
    )
    
    
    
    
@login_required
def payment_verify(request):

    order_id = request.GET.get("order_id")
    status = request.GET.get("status")  # success / fail
    payment_id = request.GET.get("pid")

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    from .services.payment import verify_payment

    success = status == "success"

    verify_payment(order, payment_id, success)

    if success:
        messages.success(request, "پرداخت با موفقیت انجام شد.")
    else:
        messages.error(request, "پرداخت ناموفق بود.")

    return redirect("orders:success", order_id=order.id)