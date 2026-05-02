from django.shortcuts import render
from django.http import HttpResponse
from .models import Customer


# Create your views here.
# This renders your main landing page (index.html)
def say_hello(request):
    return render(request, 'index.html')

# This simply renders the signup page when the link is clicked
def open_signup(request):
    return render(request, 'signup.html')

# This renders the signin page when the link is clicked
def open_signin(request):
    return render(request, 'signin.html')

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
        except:
            Customer.objects.create(
                username=username,
                password=password,
                email=email,
                mobile=mobile,
                address=address,
            )

    return render(request, 'signin.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = Customer.objects.get(username=username, password=password)
            if username == 'admin':
                return render(request, 'admin_home.html')
            return render(request, 'customer_home.html')

        except Customer.DoesNotExist:
            return render(request, 'fail.html')

    return render(request, 'signin.html')
