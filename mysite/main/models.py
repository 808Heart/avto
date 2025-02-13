from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# -----------------------
# Пользовательская модель
# -----------------------

class User(AbstractUser):
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    groups = models.ManyToManyField("auth.Group", related_name="main_users", blank=True)
    user_permissions = models.ManyToManyField(
        "auth.Permission", related_name="main_users_permissions", blank=True
    )

# -----------------------
# Бренды автомобилей
# -----------------------

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, help_text="Используется в URL")
    is_active = models.BooleanField(default=True)
    logo = models.ImageField(upload_to="brands/", blank=True, null=True)

    def __str__(self):
        return self.name

# -----------------------
# Модель автомобиля
# -----------------------

class Car(models.Model):
    name = models.CharField(max_length=100)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="cars/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    specifications = models.JSONField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.brand:
            first_word = self.name.split()[0]  
            brand_obj = Brand.objects.filter(name__iexact=first_word).first()
            if brand_obj:
                self.brand = brand_obj
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.brand.name if self.brand else 'Без бренда'})"

# -----------------------
# Изображения для автомобилей
# -----------------------

class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="cars/multiple/")

    def __str__(self):
        return f"Фото для {self.car.name}"



class TradeInRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает обработки'),
        ('approved', 'Принято'),
        ('rejected', 'Отклонено')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    mileage = models.PositiveIntegerField()
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(upload_to='trade_in_photos/', blank=True, null=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year}) - {self.user}"

class TradeInPhoto(models.Model):
    trade_in = models.ForeignKey(TradeInRequest, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="trade_in_photos/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Фото для {self.trade_in.brand} {self.trade_in.model} ({self.trade_in.year})"

class Accessory(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='accessories/', null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Корзина {self.user}"

# Функция для значения по умолчанию для content_type
def get_default_content_type():
    """Возвращает ContentType для модели Accessory."""
    return ContentType.objects.get_for_model(Accessory).pk

# Элемент корзины (универсальный для автомобилей и аксессуаров)
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, default=get_default_content_type)
    object_id = models.PositiveIntegerField(default=1)  # значение по умолчанию; для новых записей оно будет перезаписано
    item = GenericForeignKey('content_type', 'object_id')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        if self.item:
            return f"{self.quantity} x {self.item} в корзине"
        return "Неизвестный товар"

# -----------------------
# Заказы автомобилей
# -----------------------

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "В обработке"),
        ("confirmed", "Подтвержден"),
        ("delivered", "Доставлен"),
        ("canceled", "Отменен"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user} заказал {self.car.name} ({self.get_status_display()})"

# -----------------------
# Заказы аксессуаров
# -----------------------

class AccessoryOrder(models.Model):
    STATUS_CHOICES = [
        ("pending", "Ожидает обработки"),
        ("processed", "Обработан"),
        ("shipped", "Отправлен"),
        ("delivered", "Доставлен"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    accessory = models.ForeignKey(Accessory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"{self.user} - {self.accessory.name} ({self.get_status_display()})"

# -----------------------
# Заявка на тест-драйв
# -----------------------

class TestDriveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтвержден'),
        ('canceled', 'Отменен'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    phone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Тест-драйв {self.car.name} - {self.user} ({self.get_status_display()})"

# -----------------------
# Отзывы на автомобили
# -----------------------

class Review(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )

    def __str__(self):
        return f"{self.user} - {self.car.name}" if not self.parent else f"Ответ на {self.parent.id}"
