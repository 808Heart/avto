from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login
from .models import Car, Review, TradeInRequest, AccessoryOrder, Accessory, Order
from .forms import CustomUserCreationForm, ReviewForm, TradeInForm
from django.db.models import Count
from .models import Car, Brand
from django.core.paginator import Paginator
from django.db.models import Count
from .models import TestDriveRequest
from django.contrib.auth.forms import UserCreationForm
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')  # После регистрации перенаправляем на профиль
    else:
        form = UserCreationForm()

    return render(request, 'main/register.html', {'form': form})
User = get_user_model()

def car_list(request, brand_slug=None):
    cars = Car.objects.all()
    selected_brand = None

    if brand_slug:
        selected_brand = get_object_or_404(Brand, slug=brand_slug)
        cars = cars.filter(brand=selected_brand)

    search_query = request.GET.get('search', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by = request.GET.get('sort_by', '')

    if search_query:
        cars = cars.filter(name__icontains=search_query)
    if min_price:
        cars = cars.filter(price__gte=min_price)
    if max_price:
        cars = cars.filter(price__lte=max_price)

    if sort_by == 'price_asc':
        cars = cars.order_by('price')
    elif sort_by == 'price_desc':
        cars = cars.order_by('-price')
    elif sort_by == 'name_asc':
        cars = cars.order_by('name')
    elif sort_by == 'name_desc':
        cars = cars.order_by('-name')

    paginator = Paginator(cars, 6)
    page_number = request.GET.get('page')
    cars_page = paginator.get_page(page_number)

    brands = Brand.objects.annotate(car_count=Count('car')).filter(car_count__gt=0)

    return render(request, 'main/car_list.html', {
        'cars': cars_page, 
        'brands': brands,  
        'selected_brand': selected_brand,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    })

def car_detail(request, car_id):
    """ Отображает страницу автомобиля и применяет скидку по Trade-in, если заявка одобрена """
    car = get_object_or_404(Car, id=car_id)

    if 'history' not in request.session:
        request.session['history'] = []

    if car_id not in request.session['history']:
        request.session['history'].insert(0, car_id)
        if len(request.session['history']) > 5:
            request.session['history'].pop()
        request.session.modified = True

    trade_in_discount = 0

    if request.user.is_authenticated:
        trade_in_request = TradeInRequest.objects.filter(user=request.user, status='approved').first()
        if trade_in_request:
            trade_in_discount = trade_in_request.estimated_price  

    final_price = max(car.price - trade_in_discount, 0) 

    return render(request, 'main/car_detail.html', {
        'car': car,
        'final_price': final_price,
        'trade_in_discount': trade_in_discount
    })


from .models import Order

@login_required
def profile(request):
    # Получаем список избранных автомобилей
    favorite_ids = request.session.get('favorites', [])
    favorites = Car.objects.filter(id__in=favorite_ids)

    # Получаем список автомобилей для сравнения
    compare_ids = request.session.get('compare', [])
    compare = Car.objects.filter(id__in=compare_ids)

    # Получаем историю просмотров
    history_ids = request.session.get('history', [])
    history = Car.objects.filter(id__in=history_ids)

    # Получаем заявки на Trade-In
    trade_in_requests = TradeInRequest.objects.filter(user=request.user)

    accessory_orders = AccessoryOrder.objects.filter(user=request.user)


    test_drive_requests = TestDriveRequest.objects.filter(user=request.user)

    car_orders = Order.objects.filter(user=request.user)

    trade_in_discount = 0
    trade_in_request = TradeInRequest.objects.filter(user=request.user, status='approved').first()
    if trade_in_request:
        trade_in_discount = trade_in_request.estimated_price  

    for order in car_orders:
        order.final_price = max(order.car.price - trade_in_discount, 0)
        order.save()  

    return render(request, 'main/profile.html', {
        'favorites': favorites,
        'compare': compare,
        'history': history,
        'trade_in_requests': trade_in_requests,
        'accessory_orders': accessory_orders,
        'car_orders': car_orders,
        'trade_in_discount': trade_in_discount,
        'test_drive_requests': test_drive_requests,
    })


@login_required
def trade_in(request):
    if request.method == 'POST':
        # Получаем данные из формы
        brand = request.POST.get('brand')
        model = request.POST.get('model')
        year = request.POST.get('year')
        mileage = request.POST.get('mileage')
        estimated_price = request.POST.get('estimated_price')

        # Создаем заявку на Trade-In
        trade_in_request = TradeInRequest(
            user=request.user,
            brand=brand,
            model=model,
            year=year,
            mileage=mileage,
            estimated_price=estimated_price
        )
        trade_in_request.save()

        # Перенаправляем на страницу профиля с сообщением о успешной подаче заявки
        return redirect('profile')

    return render(request, 'main/trade_in.html')


@login_required
def make_order(request, car_id):
    car = Car.objects.get(id=car_id)
    trade_in_discount = 0

    trade_in_request = TradeInRequest.objects.filter(user=request.user, status='approved').first()
    if trade_in_request:
        trade_in_discount = trade_in_request.estimated_price

    order = Order.objects.create(
        user=request.user,
        car=car,
        status='pending',
        final_price=max(car.price - trade_in_discount, 0)  
    )

    return redirect('profile')

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    car_id = review.car.id
    review.delete()
    return redirect('car_detail', car_id=car_id)


def add_to_compare(request, car_id):
    if 'compare' not in request.session:
        request.session['compare'] = []

    if car_id not in request.session['compare']:
        request.session['compare'].append(car_id)
        request.session.modified = True

    return redirect('compare_cars')


def remove_from_compare(request, car_id):
    if 'compare' in request.session and car_id in request.session['compare']:
        request.session['compare'].remove(car_id)
        request.session.modified = True

    return redirect('compare_cars')


def compare_cars(request):
    car_ids = request.session.get('compare', [])
    cars = Car.objects.filter(id__in=car_ids)

    return render(request, 'main/compare.html', {'cars': cars})


def add_to_favorites(request, car_id):
    if 'favorites' not in request.session:
        request.session['favorites'] = []

    if car_id not in request.session['favorites']:
        request.session['favorites'].append(car_id)
        request.session.modified = True

    return redirect('favorites')


def remove_from_favorites(request, car_id):
    if 'favorites' in request.session and car_id in request.session['favorites']:
        request.session['favorites'].remove(car_id)
        request.session.modified = True

    return redirect('favorites')


def favorites(request):
    car_ids = request.session.get('favorites', [])
    cars = Car.objects.filter(id__in=car_ids)

    return render(request, 'main/favorites.html', {'cars': cars})


def add_accessory_to_favorites(request, accessory_id):
    if 'favorite_accessories' not in request.session:
        request.session['favorite_accessories'] = []

    if accessory_id not in request.session['favorite_accessories']:
        request.session['favorite_accessories'].append(accessory_id)
        request.session.modified = True

    return redirect('profile')


def remove_accessory_from_favorites(request, accessory_id):
    if 'favorite_accessories' in request.session and accessory_id in request.session['favorite_accessories']:
        request.session['favorite_accessories'].remove(accessory_id)
        request.session.modified = True

    return redirect('profile')


def accessories(request):
    accessories = Accessory.objects.all()
    return render(request, 'main/accessories.html', {'accessories': accessories})

@login_required
def buy_accessory(request, accessory_id):
    accessory = get_object_or_404(Accessory, id=accessory_id)

    if accessory.stock > 0:
        AccessoryOrder.objects.create(user=request.user, accessory=accessory, quantity=1)
        accessory.stock -= 1
        accessory.save()

    return redirect('profile')

@login_required
def add_to_cart(request, car_id):
    if 'cart' not in request.session:
        request.session['cart'] = {}

    cart = request.session['cart']

    if str(car_id) in cart:
        cart[str(car_id)] += 1
    else:
        cart[str(car_id)] = 1

    request.session.modified = True
    return redirect('cart') 

def remove_from_cart(request, accessory_id):
    if 'cart' in request.session and str(accessory_id) in request.session['cart']:
        del request.session['cart'][str(accessory_id)]
        request.session.modified = True

    return redirect('cart')


@login_required
def cart(request):
    cart = request.session.get('cart', {})
    car_ids = cart.keys()
    cars = Car.objects.filter(id__in=car_ids)

    cart_items = []
    total_price = 0

    for car in cars:
        quantity = cart[str(car.id)]
        total_price += car.price * quantity
        cart_items.append({'car': car, 'quantity': quantity})

    return render(request, 'main/cart.html', {'cart_items': cart_items, 'total_price': total_price})



@login_required
def cancel_order(request, order_id):
    """ Позволяет пользователю отменить заказ автомобиля """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.delete()
    return redirect('profile')
from .forms import TestDriveForm
@login_required
def test_drive(request):
    if request.method == "POST":
        form = TestDriveForm(request.POST)
        if form.is_valid():
            test_drive_request = form.save(commit=False)
            test_drive_request.user = request.user
            test_drive_request.save()
            return redirect('profile')  
    else:
        form = TestDriveForm()

    return render(request, 'main/test_drive.html', {'form': form})

@login_required
def cancel_test_drive(request, request_id):
    test_drive_request = get_object_or_404(TestDriveRequest, id=request_id, user=request.user)
    test_drive_request.status = "canceled"
    test_drive_request.save()
    return redirect('profile')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Car, Order, TradeInRequest

from django.http import JsonResponse

from django.http import JsonResponse
from .models import Car, Order, TradeInRequest
from .forms import OrderForm
@login_required
def checkout(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    # Инициализируем скидку
    trade_in_discount = 0

    # Проверяем наличие одобренной заявки Trade-in
    trade_in_request = TradeInRequest.objects.filter(user=request.user, status='approved').first()
    if trade_in_request:
        trade_in_discount = trade_in_request.estimated_price

    # Если форма отправлена
    if request.method == 'POST':
        # Получаем данные из формы и создаем заказ
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        # Рассчитываем финальную цену с учетом скидки
        final_price = max(car.price - trade_in_discount, 0)  # Не допускаем отрицательной цены

        # Создаем заказ
        order = Order.objects.create(
            user=request.user,
            car=car,
            name=name,
            email=email,
            address=address,
            phone=phone,
            final_price=final_price,  # Цена с учётом скидки
        )
        
        # Перенаправляем пользователя в его профиль
        return redirect('profile')
    
    # Отправляем данные о машине на страницу оформления
    return render(request, 'main/checkout.html', {'car': car})
