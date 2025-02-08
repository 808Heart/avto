from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Car, CarImage, Order, Review, TradeInRequest, Brand, Accessory, AccessoryOrder, TestDriveRequest
from django.utils.html import format_html

# Регистрация пользователя в админке с добавлением поля аватара
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'avatar')  # Добавляем avatar в список отображаемых полей
    search_fields = ('username', 'email')

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('avatar',)}),  # Добавляем поле аватара
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('avatar',)}),  # Добавляем поле аватара при создании нового пользователя
    )

from .models import Brand
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'logo_preview')
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ('logo_preview',)

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.logo.url)
        return "Нет логотипа"
    logo_preview.short_description = "Логотип"

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

@admin.register(TradeInRequest)
class TradeInRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'brand', 'model', 'status', 'created_at')
    list_filter = ('status',)
    actions = ['approve_trade_in', 'reject_trade_in']

    def approve_trade_in(self, request, queryset):
        queryset.update(status='approved', admin_message="Заявка одобрена")
    approve_trade_in.short_description = "Одобрить заявки на Trade-In"

    def reject_trade_in(self, request, queryset):
        queryset.update(status='rejected', admin_message="Заявка отклонена")
    reject_trade_in.short_description = "Отклонить заявки на Trade-In"

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
