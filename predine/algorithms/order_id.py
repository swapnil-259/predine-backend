import random
import string
from django.utils import timezone
from user.models import OrderDetails


def generate_unique_order_id():
    prefix = timezone.now().strftime("%Y%m%d%H%M%S")
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    order_id = f"ORD-{prefix}-{suffix}"

    while OrderDetails.objects.filter(order_id=order_id).exists():
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        order_id = f"ORD-{prefix}-{suffix}"
    return order_id
