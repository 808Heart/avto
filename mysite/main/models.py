from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="main_users",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="main_users_permissions",
        blank=True
    )

class Car(models.Model):
    name = models.CharField(max_length=100)  
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    image = models.ImageField(upload_to="cars/")  

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    car = models.ForeignKey(Car, on_delete=models.CASCADE)  
    date = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.user.username} заказал {self.car.name}"
