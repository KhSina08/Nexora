from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from django.urls import reverse

from .models import Product, ProductVariant


def get_variant(request, product_id):
    """پیدا کردن واریانت بر اساس شناسه‌های AttributeValue انتخاب‌شده"""
    attr_string = request.GET.get("attributes")

    if not attr_string:
        return JsonResponse({"error": "no attributes"}, status=400)

    attribute_ids = attr_string.split(",")

    try:
        variant = (
            ProductVariant.objects.filter(product_id=product_id, is_active=True)
            .annotate(
                matched_attributes=Count(
                    "attributes",
                    filter=Q(attributes__id__in=attribute_ids),
                ),
                total_attributes=Count("attributes"),
            )
            .filter(
                matched_attributes=len(attribute_ids),
                total_attributes=len(attribute_ids),
            )
            .first()
        )

        if not variant:
            return JsonResponse({"error": "variant not found"}, status=404)

        image = None
        variant_image = (
            variant.images.filter(is_primary=True).first()
            or variant.images.first()
        )
        if variant_image:
            image = variant_image.image.url

        discount_percent = 0
        if variant.compare_price and variant.compare_price > variant.price:
            discount_percent = round(
                ((variant.compare_price - variant.price) / variant.compare_price) * 100
            )

        return JsonResponse(
            {
                "id": variant.id,
                "price": str(variant.price),
                "compare_price": (
                    str(variant.compare_price) if variant.compare_price else None
                ),
                "discount_percent": discount_percent,
                "stock": variant.stock,
                "sku": variant.sku,
                "weight": variant.weight,
                "image": image,
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)

    variants = product.variants.filter(is_active=True)
    default_variant = variants.first()

    main_image = product.images.filter(is_main=True).first()
    gallery_images = product.images.all().order_by("-is_main", "id")

    # محصولات مرتبط (هم‌دسته) — برای سکشن «محصولات مرتبط»
    related = []
    related_qs = (
        Product.objects.filter(category=product.category, is_active=True)
        .exclude(pk=product.pk)
        .order_by("-created_at")[:8]
    )
    for p in related_qs:
        v = p.variants.filter(is_active=True).first()
        img = p.images.filter(is_main=True).first() or p.images.first()
        related.append(
            {
                "product": p,
                "display_price": f"{v.price:.0f} تومان" if v else "ناموجود",
                "old_price": (
                    f"{v.compare_price:.0f} تومان"
                    if v and v.compare_price
                    else None
                ),
                "img_url": img.image.url if img else None,
                "url": reverse("products:product_detail", args=[p.id]),
            }
        )

    return render(
        request,
        "product_detail.html",
        {
            "product": product,
            "attributes": product.product_attributes.select_related("attribute").all(),
            "main_image": main_image,
            "gallery_images": gallery_images,
            "default_variant": default_variant,
            "variants": variants,
            "related": related,
        },
    )


def product_list(request):
    """صفحه فروشگاه — فعلاً ساده؛ در اولویت ۳ با قالب shop تکمیل می‌شود."""
    products = Product.objects.filter(is_active=True)
    return render(request, "product_list.html", {"products": products})
