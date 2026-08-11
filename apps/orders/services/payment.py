import uuid


def create_payment(order):
    """
    ساخت درخواست پرداخت (Fake)
    """

    payment_id = str(uuid.uuid4())

    # اینجا در حالت واقعی API صدا می‌زنی
    # فعلاً فقط یک URL می‌سازیم

    payment_url = f"/orders/payment/{order.id}/?pid={payment_id}"

    return {
        "payment_id": payment_id,
        "payment_url": payment_url,
    }



def verify_payment(order, payment_id, success=True):
    """
    تایید پرداخت (Fake)
    """

    if success:
        order.payment_status = "paid"
        order.payment_id = payment_id
        order.save()

        return True

    else:
        order.payment_status = "failed"
        order.payment_id = payment_id
        order.save()

        return False