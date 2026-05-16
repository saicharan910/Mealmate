import razorpay
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from .models import Customer, Restaurant, Item, Cart
from django.conf import settings
import razorpay

# --- Authentication & Entry Views ---

def index(request):
    return render(request, 'index.html')

def open_signin(request):
    return render(request, 'signin.html')

def open_signup(request):
    return render(request, 'signup.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')

        try:
            Customer.objects.get(username=username)
            return HttpResponse("Duplicate username!")
        except Customer.DoesNotExist:
            Customer.objects.create(
                username=username,
                password=password,
                email=email,
                mobile=mobile,
                address=address,
            )
            return render(request, 'signin.html')
    return render(request, 'signup.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            customer = Customer.objects.get(username=username, password=password)
            if username == 'admin':
                return render(request, 'admin_home.html')
            else:
                restaurantList = Restaurant.objects.all()
                # PASSING username here is vital for your template links
                return render(request, 'customer_home.html', {"restaurantList": restaurantList, "username": username})
        except Customer.DoesNotExist:
            return render(request, 'fail.html')

    return render(request, 'signin.html')


# --- Admin Operations ---

def admin_dashboard(request):
    context = {
        'total_orders': Customer.objects.count(),
        'active_users': Customer.objects.count(),
        'daily_revenue': "4200",
    }
    return render(request, 'admin_home.html', context)

def open_add_restaurant(request):
    return render(request, 'add_restaurant.html')

def add_restaurant(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')

        try:
            Restaurant.objects.get(name=name)
            return HttpResponse("Duplicate restaurant!")
        except Restaurant.DoesNotExist:
            Restaurant.objects.create(
                name=name,
                picture=picture,
                cuisine=cuisine,
                rating=rating,
            )
            return redirect('open_show_restaurant')
    return render(request, 'add_restaurant.html')

def open_show_restaurant(request):
    restaurantList = Restaurant.objects.all()
    return render(request, 'show_restaurants.html', {"restaurantList": restaurantList})

def open_update_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    return render(request, 'update_restaurant.html', {"restaurant": restaurant})

def update_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    if request.method == 'POST':
        restaurant.name = request.POST.get('name')
        restaurant.picture = request.POST.get('picture')
        restaurant.cuisine = request.POST.get('cuisine')
        restaurant.rating = request.POST.get('rating')
        restaurant.save()
        return redirect('open_show_restaurant')

    return render(request, 'update_restaurant.html', {"restaurant": restaurant})

def delete_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    restaurant.delete()
    return redirect('open_show_restaurant')


# --- Menu Management ---

def open_update_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    # This relies on related_name="menu_items" in models.py
    itemList = restaurant.menu_items.all()
    return render(request, 'update_menu.html', {"itemList": itemList, "restaurant": restaurant})

def update_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        is_veg = request.POST.get('is_veg') == 'on'
        picture = request.POST.get('picture')

        try:
            Item.objects.get(name=name, restaurant=restaurant)
            return HttpResponse("Duplicate item in this restaurant!")
        except Item.DoesNotExist:
            Item.objects.create(
                restaurant=restaurant,
                name=name,
                description=description,
                price=price,
                is_veg=is_veg,
                picture=picture,
            )
            return redirect('open_update_menu', restaurant_id=restaurant_id)

    return render(request, 'admin_home.html')

def add_to_cart(request, item_id, username):
    item = get_object_or_404(Item, id=item_id)
    customer = get_object_or_404(Customer, username=username)
    cart, created = Cart.objects.get_or_create(customer=customer)
    cart.items.add(item)
    # Redirecting back to menu is better than a blank text page
    return redirect('view_menu', restaurant_id=item.restaurant.id, username=username)

def remove_from_cart(request, username, item_id):
    if request.method == "POST":
        customer = get_object_or_404(Customer, username=username)
        cart = Cart.objects.filter(customer=customer).first()
        if cart:
            item = get_object_or_404(Item, id=item_id)
            cart.items.remove(item)
    return redirect('show_cart', username=username)

# --- Customer Operations ---

def view_menu(request, restaurant_id, username):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    # ERROR FIX: Ensure your model HAS related_name="menu_items"
    itemList = restaurant.menu_items.all()
    return render(request, 'customer_menu.html', {
        "itemList": itemList,
        "restaurant": restaurant,
        "username": username
    })

def show_cart(request, username):
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).first()
    items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0

    return render(request, 'cart.html', {"itemList": items, "total_price": total_price, "username": username})


# --- Payment & Orders ---

def checkout(request, username):
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).first()
    total_price = cart.total_price() if cart else 0

    if total_price == 0:
        return render(request, 'checkout.html', 
                      {'error': 'Your cart is empty!', 'username': username})

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    client.session.trust_env=False  # Disable proxy detection for better reliability
    amount_paise = int(round(total_price * 100))

    #print("--- RAZORPAY DEBUG START ---")
    #print(f"Key ID being used: {settings.RAZORPAY_KEY_ID}")
    #print(f"Key Secret exists: {'Yes' if settings.RAZORPAY_KEY_SECRET else 'No'}")
    #print(f"Amount in Paise: {amount_paise}")
    #print("--- RAZORPAY DEBUG END ---")
    
    order_data = {
        'amount': amount_paise,
        'currency': 'INR',
        'payment_capture': '1',
    }

    try:
        order = client.order.create(data=order_data)
    except Exception as e:
        # Log the error and show a user-friendly message
        #return HttpResponse(f"Error creating Razorpay order: {e}")
        return render(request, 'checkout.html', {
            'username': username,
            'cart_items': cart.items.all(),
            'total_price': total_price,
            'error': 'Error creating payment order. Please try again later.',
        })


    return render(request, 'checkout.html', {
        'username': username,
        'cart_items': cart.items.all(),
        'total_price': total_price,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order_id': order['id'],
        'amount_paise': order_data['amount'],
    })

def payment_view(request):
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        data = {'razorpay_order_id': order_id, 'razorpay_payment_id': payment_id, 'razorpay_signature': signature}

        try:
            client.utility.verify_payment_signature(data)
            # Redirect to success page or orders page
            return render(request, 'success.html')
        except:
            return HttpResponse("Payment Verification Failed.")

    return redirect('customer_home')

def orders(request, username):
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).first()
    cart_items = list(cart.items.all()) if cart else []
    total_price = cart.total_price() if cart else 0

    if cart_items:
        order=razorpay.Order.objects.create(customer=customer, total_price=total_price)
        order.items.set(cart_items)
        order.save()
        
    if cart:
        cart.items.clear() # Clears cart after payment/order

    return render(request, 'orders.html', {
        'username': username,
        'customer': customer,
        'cart_items': cart_items,
        'total_price': total_price,
    })

# --- Other Operations ---


def profile(request, username):
    customer = get_object_or_404(Customer, username=username)
    return render(request, 'profile.html', {
        "username": username,
        "customer": customer
    })

from django.contrib.auth.decorators import login_required
@login_required
def profile_default(request):
    # Try to grab the username from the session or fall back to the logged-in Django auth user
    username = request.session.get('username') or (request.user.username if request.user.is_authenticated else None)
    
    if username:
        return redirect('profile', username=username)
    
    # If no session or user is found, send them back to sign in
    return redirect('open_signin')

#  Update your views.py function to accept username
def customer_home(request, username):
    # Your existing view logic here...
    
    # Example context matching your template variables:
    restaurantList = Restaurant.objects.all()
    return render(request, 'customer_home.html', {
        "restaurantList": restaurantList, 
        "username": username
    })



# Update this view inside views.py
def save_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        
        if username:
            customer = get_object_or_404(Customer, username=username)
            customer.mobile = mobile
            customer.address = address
            customer.save()
            return redirect('profile', username=username)
            
    return redirect('open_signin')