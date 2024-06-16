from django.db import models
from Login.models import BaseModel, Dropdown, User


class OwnerDetails(BaseModel):
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='Owner_User')
    restaurant_name = models.CharField(max_length=50, null=False)
    address = models.TextField(null=False)
    restaurant_type = models.ForeignKey(
        Dropdown, on_delete=models.SET_NULL, null=True, related_name='Owner_Restaurant')
