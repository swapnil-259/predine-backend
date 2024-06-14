from django.db import models
from django.contrib.auth.models import User, AbstractUser


class BaseModel(models.Model):
    deleted_status = models.BooleanField(default=False)
    created_time = models.DateTimeField(auto_now_add=True)
    deleted_time = models.DateTimeField(null=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    phone_number = models.PositiveBigIntegerField(null=False)


class Dropdown(BaseModel):
    parent = models.CharField(max_length=50)
    child = models.ForeignKey('DropDown', on_delete=models.SET_NULL, null=True)
    can_edit = models.BooleanField(default=False)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class LeftPanel(BaseModel):
    parent = models.CharField(max_length=50, null=False)
    child = models.ForeignKey(
        'LeftPanel', on_delete=models.SET_NULL, null=True)
    icon = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)


class OwnerDetails(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    restaurant_name = models.CharField(max_length=50, null=False)
    address = models.TextField(null=False)
    type = models.ForeignKey(Dropdown, on_delete=models.SET_NULL, null=True)


class Roles(BaseModel):
    role_name = models.CharField(max_length=50, null=False)


class UserRole(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    role = models.ForeignKey(Roles, on_delete=models.SET_NULL, null=True)


class OTPDetails(BaseModel):
    otp = models.PositiveIntegerField(default=0)
    email = models.EmailField(null=True)
    verified_status = models.BooleanField(default=False)
