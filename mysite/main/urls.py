from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import accessory_list, add_to_cart


urlpatterns = [
    path('', views.car_list, name='car_list'),
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    path('order/<int:car_id>/', views.make_order, name='make_order'),
    path('profile/', views.profile, name='profile'),
    
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # Убираем next_page, используем из settings.py
    
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('compare/', views.compare_cars, name='compare_cars'),
    path('add_to_compare/<int:car_id>/', views.add_to_compare, name='add_to_compare'),
    path('remove_from_compare/<int:car_id>/', views.remove_from_compare, name='remove_from_compare'),
    path('accessories/', views.accessory_list, name='accessories'),
    path('favorites/', views.favorites, name='favorites'),
    path('add_to_favorites/<int:car_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('remove_from_favorites/<int:car_id>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('trade-in/', views.trade_in, name='trade_in'),
    path('accessory/<int:accessory_id>/add_to_cart/', views.add_to_cart, name='add_to_cart_accessory'),
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:car_id>/', views.add_to_cart, name='add_to_cart_car'),
    path('remove_from_cart/<int:accessory_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('buy_accessory/<int:accessory_id>/', views.buy_accessory, name='buy_accessory'),
    path('add_accessory_to_favorites/<int:accessory_id>/', views.add_accessory_to_favorites, name='add_accessory_to_favorites'),
    path('remove_accessory_from_favorites/<int:accessory_id>/', views.remove_accessory_from_favorites, name='remove_accessory_from_favorites'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('brand/<slug:brand_slug>/', views.car_list, name='brand_cars'),
    path('test-drive/', views.test_drive, name='test_drive'),
    path('cancel_test_drive/<int:request_id>/', views.cancel_test_drive, name='cancel_test_drive'),
    path('checkout/<int:car_id>/', views.checkout, name='checkout'),
    path('accessory/<int:accessory_id>/add_to_cart/', views.add_to_cart, name='add_to_cart'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
