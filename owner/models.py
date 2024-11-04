from django.db import models
from Login.models import BaseModel, Dropdown, UserRole
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
    diet = models.ForeignKey(
        Dropdown, on_delete=models.SET_NULL, related_name='dish_diet', null=True)
    recommended = models.BooleanField(default=False)

class ChefRestaurantMapping(BaseModel):
    chef = models.ForeignKey(UserRole,on_delete=models.SET_NULL,null=True)
    restaurant =models.ForeignKey(OwnerDetails,on_delete=models.SET_NULL,null=True)
