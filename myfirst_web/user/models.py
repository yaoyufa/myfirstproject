from django.db import models
from django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel
class User(AbstractUser,BaseModel):
    user_phone=models.CharField(max_length=11,default='')
    user_address = models.CharField(max_length=100, default='')
    class Mate:
        db_table="user"
class Address(models.Model):
    user_address=models.CharField(max_length=50)
    user_postcode=models.CharField(max_length=6)
    user_phone=models.CharField(max_length=11)
    user_recipient=models.CharField(max_length=50)
    a_username = models.ForeignKey('User')
    class Mate:
        db_table="address"

class AreaInfo(models.Model):
    atitle = models.CharField(max_length=30)
    aParent = models.ForeignKey('self', null=True, blank=True)
    class Mate:
        db_table="areainfo"