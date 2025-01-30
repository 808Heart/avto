from django.shortcuts import render, get_object_or_404, redirect
from .models import Car
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm 

def car_list(request):
    cars = Car.objects.all()  
    return render(request, 'main/car_list.html', {'cars': cars})

def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    return render(request, 'main/car_detail.html', {'car': car})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Car, Order

@login_required 
def make_order(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if Order.objects.filter(user=request.user, car=car).exists():
        return render(request, 'main/order_exists.html', {'car': car})

    Order.objects.create(user=request.user, car=car)

    return redirect('profile') 

User = get_user_model()  

@login_required
def profile(request):
    user = User.objects.get(username=request.user.username)  
    orders = Order.objects.filter(user=user)  
    return render(request, 'main/profile.html', {'orders': orders})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'main/register.html', {'form': form})