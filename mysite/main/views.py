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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')  # После регистрации перенаправляем на профиль
    else:
        form = CustomUserCreationForm()

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
    """ Отображает страницу автомобиля и применяет скидку по Trade-in, если одобренная заявка существует """
    car = get_object_or_404(Car, id=car_id)

    # Работа с историей просмотров
    if 'history' not in request.session:
        request.session['history'] = []
    if car_id not in request.session['history']:
        request.session['history'].insert(0, car_id)
        if len(request.session['history']) > 5:
            request.session['history'].pop()
        request.session.modified = True

    trade_in_discount = 0
    if request.user.is_authenticated:
        # Получаем первую одобренную и не использованную заявку Trade-in
        trade_in_request = TradeInRequest.objects.filter(user=request.user, status='approved', used=False).first()
        if trade_in_request:
            # Заменяем desired_discount на estimated_price, так как поле называется именно так
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
    # Избранные автомобили (хранятся в сессии по ключу 'favorites')
    favorite_ids = request.session.get('favorites', [])
    favorites = Car.objects.filter(id__in=favorite_ids)

    # Избранные аксессуары (если они хранятся в сессии, например, по ключу 'favorite_accessories')
    favorite_accessory_ids = request.session.get('favorite_accessories', [])
    favorite_accessories = Accessory.objects.filter(id__in=favorite_accessory_ids)

    # Автомобили для сравнения (хранятся в сессии по ключу 'compare')
    compare_ids = request.session.get('compare', [])
    compare = Car.objects.filter(id__in=compare_ids)

    # История просмотров (хранятся в сессии по ключу 'history')
    history_ids = request.session.get('history', [])
    history = Car.objects.filter(id__in=history_ids)

    # Заявки на Trade-In
    trade_in_requests = TradeInRequest.objects.filter(user=request.user)

    # Заказы аксессуаров
    accessory_orders = AccessoryOrder.objects.filter(user=request.user)

    # Заявки на тест-драйв
    test_drive_requests = TestDriveRequest.objects.filter(user=request.user)

    # Заказы автомобилей
    car_orders = Order.objects.filter(user=request.user)

    # Вычисляем скидку по Trade-In
    trade_in_discount = 0
    # Ищем первую одобренную заявку, которая ещё не использована
    trade_in_request = TradeInRequest.objects.filter(user=request.user, status='approved', used=False).first()
    if trade_in_request:
        trade_in_discount = trade_in_request.estimated_price

    # Обновляем окончательную цену для заказов, если скидка применяется
    for order in car_orders:
        order.final_price = max(order.car.price - trade_in_discount, 0)
        order.save()

    context = {
        'favorites': favorites,
        'favorite_accessories': favorite_accessories,
        'compare': compare,
        'history': history,
        'trade_in_requests': trade_in_requests,
        'accessory_orders': accessory_orders,
        'car_orders': car_orders,
        'trade_in_discount': trade_in_discount,
        'test_drive_requests': test_drive_requests,
    }
    return render(request, 'main/profile.html', context)

def compare_cars(request):
    # Получаем список ID автомобилей для сравнения из сессии
    car_ids = request.session.get('compare', [])
    cars = list(Car.objects.filter(id__in=car_ids))
    
    # Вычисляем общие характеристики
    common_specs = {}
    if cars:
        # Собираем спецификации для тех автомобилей, у которых они заданы
        specs_list = [car.specifications for car in cars if car.specifications]
        if specs_list:
            common_keys = set(specs_list[0].keys())
            for specs in specs_list[1:]:
                common_keys &= set(specs.keys())
            for key in common_keys:
                common_specs[key] = [car.specifications.get(key, '—') if car.specifications else '—' for car in cars]
    
    return render(request, 'main/compare.html', {
        'cars': cars,
        'common_specs': common_specs,
    })


from .models import TradeInPhoto 
@login_required
def trade_in(request):
    if request.method == "POST":
        form = TradeInForm(request.POST, request.FILES)
        if form.is_valid():
            trade_in_request = form.save(commit=False)
            trade_in_request.user = request.user
            trade_in_request.save()

            if hasattr(trade_in_request, 'photos'):
                for photo in request.FILES.getlist('photos'):
                    TradeInPhoto.objects.create(trade_in_request=trade_in_request, image=photo)

            return redirect('profile')
    else:
        form = TradeInForm()

    return render(request, 'main/trade_in.html', {'form': form})
@login_required
def manage_trade_in(request):
    if request.user.is_staff:
        trade_in_requests = TradeInRequest.objects.filter(status='pending')

        if request.method == "POST":
            trade_in_request_id = request.POST.get('trade_in_request_id')
            status = request.POST.get('status')
            admin_message = request.POST.get('admin_message')

            trade_in_request = get_object_or_404(TradeInRequest, id=trade_in_request_id)
            trade_in_request.status = status
            trade_in_request.admin_message = admin_message
            trade_in_request.save()

            if status == 'approved':
                car = Car.objects.get(id=request.POST.get('car_id'))
                car.price -= trade_in_request.estimated_price  # Применяем скидку
                car.save()

            return redirect('manage_trade_in')

        return render(request, 'main/manage_trade_in.html', {'trade_in_requests': trade_in_requests})
    else:
        return redirect('profile')
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

@login_required
def update_nickname(request):
    if request.method == 'POST':
        new_nickname = request.POST.get('nickname')
        if new_nickname:
            user = request.user
            user.username = new_nickname
            user.save()
    return redirect('profile')

def add_to_compare(request, car_id):
    if 'compare' not in request.session:
        request.session['compare'] = []
    if car_id not in request.session['compare']:
        request.session['compare'].append(car_id)
        request.session.modified = True
    return redirect(request.META.get('HTTP_REFERER', 'profile'))

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart')


def compare_cars(request):
    # Получаем список ID автомобилей для сравнения из сессии
    car_ids = request.session.get('compare', [])
    cars = list(Car.objects.filter(id__in=car_ids))
    
    common_specs = {}
    if cars:
        specs_list = [car.specifications for car in cars if car.specifications]
        if specs_list:
            common_keys = set(specs_list[0].keys())
            for specs in specs_list[1:]:
                common_keys &= set(specs.keys())
            for key in common_keys:
                common_specs[key] = [car.specifications.get(key, '—') if car.specifications else '—' for car in cars]
    
    return render(request, 'main/compare.html', {
        'cars': cars,
        'common_specs': common_specs,
    })

@login_required
def remove_from_compare(request, car_id):
    """
    Функция удаляет автомобиль из списка сравнения, хранящегося в сессии.
    car_id — идентификатор автомобиля, который нужно удалить.
    """
    # Получаем список автомобилей для сравнения из сессии (если он отсутствует, получаем пустой список)
    compare_list = request.session.get('compare', [])
    
    # Если переданный car_id есть в списке, удаляем его
    if car_id in compare_list:
        compare_list.remove(car_id)
        request.session['compare'] = compare_list
        request.session.modified = True

    # Перенаправляем пользователя на страницу профиля (или другую, где отображается список сравнения)
    return redirect('profile')
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


from django.contrib.contenttypes.models import ContentType
from .models import Cart, CartItem, Car, Accessory

@login_required
def add_to_cart(request, object_id):
    # Сначала пробуем GET, если нет – пробуем POST
    item_type = request.GET.get('type') or request.POST.get('type')
    
    if item_type == 'car':
        model_class = Car
    elif item_type == 'accessory':
        model_class = Accessory
    else:
        return redirect('cart')
    
    # Остальная логика остается без изменений:
    item_object = get_object_or_404(model_class, id=object_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    content_type = ContentType.objects.get_for_model(model_class)
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        content_type=content_type,
        object_id=item_object.id
    )
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')

@login_required
def cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart_items = cart.items.all()
        total_price = 0
        for cart_item in cart_items:
            # Предполагаем, что и Car, и Accessory имеют поля name и price
            if hasattr(cart_item.item, 'price'):
                total_price += cart_item.item.price * cart_item.quantity
    else:
        cart_items = []
        total_price = 0
    return render(request, 'main/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

@login_required
def cancel_order(request, order_id):
    """Позволяет пользователю отменить заказ автомобиля"""
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

    trade_in_discount = 0

    trade_in_request = TradeInRequest.objects.filter(user=request.user, status='approved', used=False).first()
    if trade_in_request:
        trade_in_discount = trade_in_request.estimated_price

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        final_price = max(car.price - trade_in_discount, 0)

        order = Order.objects.create(
            user=request.user,
            car=car,
            name=name,
            email=email,
            address=address,
            phone=phone,
            final_price=final_price
        )

        if trade_in_request:
            trade_in_request.used = True
            trade_in_request.save()

        return redirect('profile')

    return render(request, 'main/checkout.html', {'car': car})


from django.shortcuts import render
from .models import Accessory

def accessory_list(request):
    accessories = Accessory.objects.all()
    return render(request, 'main/accessory_list.html', {'accessories': accessories})

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart')

from .forms import AvatarUpdateForm

@login_required
def update_avatar(request):
    if request.method == 'POST':
        form = AvatarUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  
    else:
        form = AvatarUpdateForm(instance=request.user)
    return render(request, 'main/update_avatar.html', {'form': form})