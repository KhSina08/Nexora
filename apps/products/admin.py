from django.contrib import admin

from .models import (
    Category,
    Brand,
    Product,
    ProductImage,
    Attribute,
    AttributeValue,
    ProductVariant,
    ProductAttribute,
    VariantImage,
)


admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(ProductImage)
admin.site.register(Attribute)




class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant

    
    fk_name = "product"   # 🔥 اینو اضافه کن
    
    fields = (
        "attributes",
        "price",
        "compare_price",
        "stock",
        "manage_stock",
        "weight",
        "sku",
        "is_active",
    )

    extra = 1

    filter_horizontal = ("attributes",)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "attributes":
            try:
                object_id = request.resolver_match.kwargs.get("object_id")

                if object_id:
                    product = Product.objects.get(pk=object_id)

                    attrs = product.product_attributes.values_list(
                        "attribute",
                        flat=True
                    )

                    # بعداً اینجا فیلتر AttributeValue اضافه می‌شود

            except Exception:
                pass

        return super().formfield_for_manytomany(
            db_field,
            request,
            **kwargs
        )


class VariantImageInline(admin.TabularInline):
    model = VariantImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductImageInline,
        ProductAttributeInline,
        ProductVariantInline,
    ]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    inlines = [
        VariantImageInline,
    ]

    list_display = (
        "product",
        "sku",
        "price",
        "stock",
        "is_active",
    )


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = (
        "attribute",
        "value",
    )