from django.db import models

from execution.models import OwnerDetails
from Login.models import BaseModel, Dropdown, User
from owner.models import Dish


class OrderDetails(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    order_id = models.CharField(max_length=100, null=True)
    payment_status = models.ForeignKey(Dropdown, on_delete=models.SET_NULL, null=True)
    payment_id = models.CharField(max_length=150, null=True)
    payment_signature = models.CharField(max_length=200, null=True)
    total_amount = models.BigIntegerField(default=0)
    order_time = models.DateTimeField(null=True)
    razorpay_order_id = models.CharField(max_length=200, null=True)
    restaurant = models.ForeignKey(OwnerDetails, on_delete=models.SET_NULL, null=True)


class OrderDishDetails(models.Model):
    order = models.ForeignKey(OrderDetails, on_delete=models.SET_NULL, null=True)
    dish = models.ForeignKey(Dish, on_delete=models.SET_NULL, null=True)
    quantity = models.BigIntegerField(default=1)
    amount = models.BigIntegerField(default=0)
    cancel = models.BooleanField(default=False)


class OrderLogs(models.Model):
    order = models.ForeignKey(OrderDetails, on_delete=models.SET_NULL, null=True)
    level = models.IntegerField(default=1)
    order_status = models.ForeignKey(Dropdown, on_delete=models.SET_NULL, null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True,null=True)
    remark = models.CharField(max_length=200, null=True)
