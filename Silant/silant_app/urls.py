# urls.py
from django.urls import path
from .views import MachineListView

urlpatterns = [
    path('', MachineListView.as_view(), name='machine-list'),
    # Добавьте другие маршруты, если это необходимо
]
