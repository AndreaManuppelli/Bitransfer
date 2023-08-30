from django.db import models
from uuid import uuid4
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class CustomUser(AbstractUser):
    btc_balance = models.FloatField()
    plan = models.IntegerField()
    remaining_minutes_plan = models.IntegerField()

    objects = CustomUserManager()
    
class CoinsRate(models.Model):
    bitcoin = models.FloatField()
    dogecoin = models.FloatField()
    dash = models.FloatField()
    litecoin = models.FloatField()
    date = models.DateTimeField()
    fee_btc_per_byte = models.IntegerField()


class Payments(models.Model):
    id = models.UUIDField(primary_key=True)
    coin = models.CharField(max_length=25)
    label = models.CharField(max_length=10000)
    address = models.CharField(max_length=150)
    owner = models.CharField(max_length=150)
    creation = models.DateTimeField()
    amount = models.FloatField()
    paid = models.BooleanField()
    paid_not_confirmed = models.BooleanField()
    paid_not_confirmed_incorrect = models.BooleanField()
    withdrawn = models.BooleanField()
    incorrect_payment = models.BooleanField()
    recived = models.FloatField()
    recived_unconfirmed = models.FloatField()
    signal_url = models.CharField(max_length=2000, null=True)
    redirect_url = models.CharField(max_length=2000, null=True)
    tx_confirmations = models.IntegerField()


class PurchasedPlans(models.Model):
    id = models.UUIDField(primary_key=True)
    username_buyer = models.CharField(max_length=500)
    address = models.CharField(max_length=150)
    creation = models.DateTimeField()
    amount = models.FloatField()
    paid = models.BooleanField()
    plan_id = models.IntegerField()
    withdrawn = models.BooleanField()
    incorrect_payment = models.BooleanField()
    recived = models.FloatField()
    datetime_payment_confirmed = models.DateTimeField(null=True)



class IncorrectPayments(models.Model):
    id = models.UUIDField(primary_key=True)
    coin = models.CharField(max_length=25)
    amount = models.FloatField()
    recived = models.FloatField()
    returned = models.BooleanField()


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True)
    amount = models.FloatField()
    to = models.CharField(max_length=150)
    date = models.DateTimeField()


