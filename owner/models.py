from django.db import models
from Login.models import BaseModel, Dropdown
from execution.models import OwnerDetails
from predine.constants import functions


class Dish(BaseModel):
    restaurant = models.ForeignKey(
        OwnerDetails, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=80, null=True)
    description = models.TextField(null=False)
    price = models.PositiveIntegerField(null=False)
    category = models.ForeignKey(
        Dropdown, on_delete=models.SET_NULL, null=True)
    image = models.FileField(upload_to=functions.get_dish_img, null=False)
    preparation_time = models.PositiveIntegerField(null=False)
