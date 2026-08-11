from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from .models import ProductVariant


@receiver(m2m_changed, sender=ProductVariant.attributes.through)
def prevent_duplicate_variant(sender, instance, action, **kwargs):

    if action == "post_add":

        current_attributes = set(
            instance.attributes.values_list("id", flat=True)
        )

        variants = ProductVariant.objects.filter(
            product=instance.product
        ).exclude(
            id=instance.id
        )

        for variant in variants:
            variant_attributes = set(
                variant.attributes.values_list("id", flat=True)
            )

            if current_attributes == variant_attributes:
                raise ValidationError(
                    "This variant already exists."
                )