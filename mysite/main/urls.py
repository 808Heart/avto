from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Главная страница – список автомобилей
    path('', views.car_list, name='car_list'),
    # Детали автомобиля
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    # Оформление заказа на автомобиль (если используется отдельно)
    path('order/<int:car_id>/', views.make_order, name='make_order'),
    # Профиль пользователя
    path('profile/', views.profile, name='profile'),
    # Регистрация, вход, выход
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Отзывы и сравнение
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('compare/', views.compare_cars, name='compare_cars'),
    path('add_to_compare/<int:car_id>/', views.add_to_compare, name='add_to_compare'),
    path('remove_from_compare/<int:car_id>/', views.remove_from_compare, name='remove_from_compare'),
    # Каталог аксессуаров и избранное
    path('accessories/', views.accessory_list, name='accessories'),
    path('favorites/', views.favorites, name='favorites'),
    path('add_to_favorites/<int:car_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('remove_from_favorites/<int:car_id>/', views.remove_from_favorites, name='remove_from_favorites'),
    # Trade-In заявки
    path('trade-in/', views.trade_in, name='trade_in'),
    # Универсальный маршрут для добавления в корзину (автомобиль или аксессуар)
    path('add_to_cart/<int:object_id>/', views.add_to_cart, name='add_to_cart'),
    # Страница корзины
    path('cart/', views.cart, name='cart'),
    # Удаление элемента корзины по id элемента корзины
    path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    # Дополнительные функции
    path('buy_accessory/<int:accessory_id>/', views.buy_accessory, name='buy_accessory'),
    path('add_accessory_to_favorites/<int:accessory_id>/', views.add_accessory_to_favorites, name='add_accessory_to_favorites'),
    path('remove_accessory_from_favorites/<int:accessory_id>/', views.remove_accessory_from_favorites, name='remove_accessory_from_favorites'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('brand/<slug:brand_slug>/', views.car_list, name='brand_cars'),
    path('test-drive/', views.test_drive, name='test_drive'),
    path('cancel_test_drive/<int:request_id>/', views.cancel_test_drive, name='cancel_test_drive'),
    path('checkout/<int:car_id>/', views.checkout, name='checkout'),
    # Универсальное оформление заказа для всей корзины (автомобили и аксессуары)
    path('checkout_cart/', views.checkout_cart, name='checkout_cart'),
    # Обновление аватара и никнейма
    path('update-avatar/', views.update_avatar, name='update_avatar'),
    path('update-nickname/', views.update_nickname, name='update_nickname'),
    path('cancel_accessory_order/<int:order_id>/', views.cancel_accessory_order, name='cancel_accessory_order'),
    # Пример универсального маршрута для добавления в корзину:
    path('add_to_cart/<int:object_id>/', views.add_to_cart, name='add_to_cart'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)