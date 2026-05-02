from django.urls import path
from . import views

urlpatterns = [
    path('', views.say_hello, name="say_hello"),
    path('open_signup', views.open_signup, name="open_signup"),
    path('open_signin', views.open_signin, name="open_signin"),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
]
