# urls.py
from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', MachineListView.as_view(), name='machine-list'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'), 
]
