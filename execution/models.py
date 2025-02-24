from django.db import models

from Login.models import BaseModel, Dropdown, Roles, User
from predine.constants import functions


class OwnerDetails(BaseModel):
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="Owner_User"
    )
    restaurant_name = models.CharField(max_length=50, null=False)
    address = models.TextField(null=False)
    restaurant_type = models.ForeignKey(
        Dropdown, on_delete=models.SET_NULL, null=True, related_name="Owner_Restaurant"
    )
    owner_role = models.ForeignKey(Roles, on_delete=models.SET_NULL, null=True)
    restaurant_pic = models.ImageField(
        upload_to=functions.get_restaurant_img, null=True
    )
    acc_holder_name = models.CharField(max_length=100, null=True)
    acc_ifsc_code = models.CharField(max_length=150, null=True)
    acc_number = models.PositiveBigIntegerField(null=True)
    is_password_updated = models.BooleanField(default=False)
    account_status = models.BooleanField(default=False)
    is_open = models.BooleanField(default=True)


class DashboardMapping(BaseModel):
    category = models.ForeignKey(
        Dropdown, on_delete=models.SET_NULL, null=True, related_name="dash_map_category"
    )
    image = models.FileField(upload_to="", null=True)
