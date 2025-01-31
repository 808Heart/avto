from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Car, CarImage, Order, Review, TradeInRequest, Brand, Accessory, AccessoryOrder, TestDriveRequest

# Регистрация пользователя в админке
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')

# Регистрация брендов в админке
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {"slug": ("name",)}

# Инлайны для изображений автомобилей
class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 3

# Регистрация автомобилей в админке
@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "price")
    list_filter = ('brand',)
    search_fields = ("name", "brand__name")
    inlines = [CarImageInline]

# Регистрация заказов автомобилей в админке
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'date', 'status', 'final_price')
    list_filter = ('status',)
    search_fields = ('user__username', 'car__name')
    ordering = ('-date',)
    list_editable = ('status',)

# Регистрация отзывов в админке
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'rating', 'created_at')
    search_fields = ('user__username', 'car__name')
    ordering = ('-created_at',)

# Регистрация Trade-In заявок в админке
@admin.register(TradeInRequest)
class TradeInRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'brand', 'model', 'year', 'mileage', 'estimated_price', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('brand', 'model', 'user__username')
    ordering = ('-created_at',)
    actions = ['approve_trade_in', 'reject_trade_in']

    def approve_trade_in(self, request, queryset):
        for trade_request in queryset:
            trade_request.status = 'approved'
            trade_request.admin_message = "Ваш Trade-in одобрен! Сумма вычтена из стоимости автомобиля."
            trade_request.save()

    def reject_trade_in(self, request, queryset):
        for trade_request in queryset:
            trade_request.status = 'rejected'
            trade_request.admin_message = "К сожалению, ваш Trade-in отклонён."
            trade_request.save()

    approve_trade_in.short_description = "Одобрить Trade-in"
    reject_trade_in.short_description = "Отклонить Trade-in"

# Регистрация аксессуаров в админке
@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock')
    search_fields = ('name',)
    ordering = ('price',)

# Регистрация заказов аксессуаров
@admin.register(AccessoryOrder)
class AccessoryOrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'accessory', 'quantity', 'date', 'status')
    list_filter = ('status',)
    search_fields = ('user__username', 'accessory__name')
    ordering = ('-date',)
    actions = ['mark_as_processed', 'mark_as_shipped', 'mark_as_delivered']

    def mark_as_processed(self, request, queryset):
        queryset.update(status='processed')
    mark_as_processed.short_description = "Пометить как 'Обработан'"

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
    mark_as_shipped.short_description = "Пометить как 'Отправлен'"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
    mark_as_delivered.short_description = "Пометить как 'Доставлен'"

# Регистрация заявок на тест-драйв
@admin.register(TestDriveRequest)
class TestDriveRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'date', 'time', 'status')
    list_filter = ('status',)
    search_fields = ('user__username', 'car__name')
    ordering = ('-date',)
    actions = ['confirm_test_drive', 'cancel_test_drive']

    def confirm_test_drive(self, request, queryset):
        queryset.update(status='confirmed')
    confirm_test_drive.short_description = "Подтвердить тест-драйв"

    def cancel_test_drive(self, request, queryset):
        queryset.update(status='canceled')
    cancel_test_drive.short_description = "Отменить тест-драйв"

# Регистрация изображения автомобиля
admin.site.register(CarImage)
