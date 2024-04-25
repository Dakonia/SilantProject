# forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm
from .models import *

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)



class MachineForm(ModelForm):
    class Meta:
        model = Machine
        fields = '__all__'
        widgets = {
            'shipment_date': forms.DateInput(attrs={'type': 'date'}),
        }


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = '__all__'
        widgets = {
            'maintenance_date': forms.DateInput(attrs={'type': 'date'}),
            'order_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ReclamationForm(forms.ModelForm):
    class Meta:
        model = Reclamation
        # fields = '__all__'
        exclude = ['nonuse_time']
        widgets = {
            'failure_date' : forms.DateInput(attrs={'type':'date'}),
            'repair_date' : forms.DateInput(attrs={'type':'date'})
        }