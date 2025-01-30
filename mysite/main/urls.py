from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.car_list, name='car_list'),
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    path('order/<int:car_id>/', views.make_order, name='make_order'),
    path('profile/', views.profile, name='profile'),
    
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html', next_page='profile'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
