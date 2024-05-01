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
            'configuration': forms.Textarea(attrs={'rows': 7, 'cols': 35}),
            'shipment_date': forms.DateInput(attrs={'type': 'date'}),
        }

class MaintenanceFormEdit(MachineForm):
    class Meta:
        model= Maintenance
        exclude = ['reference_entity', 'machine']
        fields = '__all__'
        widgets = {
            'shipment_date': forms.DateInput(attrs={'type': 'date'}),
        }
class ReclamationFormEdit(MachineForm):
    class Meta:
        model= Reclamation
        exclude = ['reference_entity', 'machine', 'nonuse_time']
        fields = '__all__'
        widgets = {
            'failure_description' : forms.Textarea(attrs={'rows': 7, 'cols': 35}),
            'spare_parts' : forms.Textarea(attrs={'rows': 7, 'cols': 35}),
            'shipment_date': forms.DateInput(attrs={'type': 'date'}),
        }


class MachineFormEdit(ModelForm):
    class Meta:
        model = Machine
        exclude = ['reference_entity']
        fields = '__all__'
        widgets = {
            'configuration': forms.Textarea(attrs={'rows': 7, 'cols': 35}),
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
            'failure_description' : forms.Textarea(attrs={'rows': 7, 'cols': 35}),
            'spare_parts' : forms.Textarea(attrs={'rows': 7, 'cols': 35}),
            'failure_date' : forms.DateInput(attrs={'type':'date'}),
            'repair_date' : forms.DateInput(attrs={'type':'date'})
        }