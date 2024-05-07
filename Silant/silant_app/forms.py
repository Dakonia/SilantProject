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
        exclude = ['reference_entity']
        fields = '__all__'
        widgets = { 
            'configuration': forms.Textarea(attrs={'rows': 7, 'cols': 35}),
            'shipment_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        reference_entity = ReferenceEntity.objects.get(name="Машина")
        instance.reference_entity = reference_entity
        if commit:
            instance.save()
        return instance 

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
        exclude = ['reference_entity']
        widgets = {
            'maintenance_date': forms.DateInput(attrs={'type': 'date'}),
            'order_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            if user.groups.filter(name='Client').exists():
                self.fields['machine'].queryset = Machine.objects.filter(client__user=user)
            elif user.groups.filter(name='Service').exists():
                self.fields['machine'].queryset = Machine.objects.filter(service_department__user=user) 
            elif user.groups.filter(name="Manager").exists():
                self.fields['machine'].queryset = Machine.objects.all()
    

    def save(self, commit=True):
        instance = super().save(commit=False)
        reference_entity = ReferenceEntity.objects.get(name="Техническое обслуживание")
        instance.reference_entity = reference_entity
        if commit:
            instance.save()
        return instance     

class ReclamationForm(forms.ModelForm):
    class Meta:
        model = Reclamation
        # fields = '__all__'
        exclude = ['nonuse_time', 'reference_entity']
        widgets = {
            'failure_description' : forms.Textarea(attrs={'rows': 7, 'cols': 35}),
            'spare_parts' : forms.Textarea(attrs={'rows': 7, 'cols': 35}),
            'failure_date' : forms.DateInput(attrs={'type':'date'}),
            'repair_date' : forms.DateInput(attrs={'type':'date'})
        }
   

    def save(self, commit=True):
        instance = super().save(commit=False)
        reference_entity = ReferenceEntity.objects.get(name="Рекламации")
        instance.reference_entity = reference_entity
        if commit:
            instance.save()
        return instance 

class EngineForm(forms.ModelForm):
    class Meta:
        model = EngineModel 
        fields = '__all__' 
        exclude = ['reference_entity'] 
        widgets = {
            'configuration': forms.Textarea(attrs={'rows': 7, 'cols': 20}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        reference_entity = ReferenceEntity.objects.get(name="Модель двигателя")
        instance.reference_entity = reference_entity
        if commit:
            instance.save()
        return instance     

class MachineModelFrom(ModelForm):
    class Meta:
        model = MachineModel
        exclude = ['reference_entity'] 
        fields = '__all__'  
        widgets = {
            'configuration': forms.Textarea(attrs={'rows': 7, 'cols': 20}),
        }  

    def save(self, commit=True):
        instance = super().save(commit=False)
        reference_entity = ReferenceEntity.objects.get(name="Модель техники")
        instance.reference_entity = reference_entity
        if commit:
            instance.save()
        return instance         

class TransmissionForm(ModelForm):
    class Meta:
        model = TransmissionModel
        fields = '__all__'
        exclude = ['reference_entity'] 
        widgets = {
            'configuration': forms.Textarea(attrs={'rows': 7, 'cols': 20}),
        }  

    def save(self, commit=True):
        instance = super().save(commit=False)
        reference_entity = ReferenceEntity.objects.get(name="Модель трансмиссии")
        instance.reference_entity = reference_entity
        if commit:
            instance.save()
        return instance  
    

class DriveAxleForm(ModelForm):
    class Meta:
        model = DriveAxleModel
        exclude = ['reference_entity'] 
        fields = '__all__'
        widgets = {
            'configuration': forms.Textarea(attrs={'rows': 7, 'cols': 20}),
        } 
    def save(self, commit=True):
        instance = super().save(commit=False)
        reference_entity = ReferenceEntity.objects.get(name="Модель ведущего моста")
        instance.reference_entity = reference_entity
        if commit:
            instance.save()
        return instance  
    
class SteerAxleForm(ModelForm):
    class Meta:
        model = SteerAxleModel
        exclude = ['reference_entity'] 
        fields = '__all__' 
        widgets = {
            'configuration': forms.Textarea(attrs={'rows': 7, 'cols': 20}),
        } 
    def save(self, commit=True):
        instance = super().save(commit=False)
        reference_entity = ReferenceEntity.objects.get(name="Модель управляемого моста")
        instance.reference_entity = reference_entity
        if commit:
            instance.save()
        return instance  
    
class MaintenanceTypeForm(ModelForm):
    class Meta:
        model = MaintenanceType
        exclude = ['reference_entity'] 
        fields = '__all__'
        widgets = {
            'configuration': forms.Textarea(attrs={'rows': 7, 'cols': 20}),
        } 
    def save(self, commit=True):
        instance = super().save(commit=False)
        reference_entity = ReferenceEntity.objects.get(name="Вид ТО")
        instance.reference_entity = reference_entity
        if commit:
            instance.save()
        return instance  
    

class ServiceToForm(ModelForm):
    class Meta:
        model = ServiceTO
        exclude = ['reference_entity'] 
        fields = '__all__' 
        widgets = {
            'configuration': forms.Textarea(attrs={'rows': 7, 'cols': 20}),
        }  
    def save(self, commit=True):
        instance = super().save(commit=False)
        reference_entity = ReferenceEntity.objects.get(name="Организация проводившая ТО")
        instance.reference_entity = reference_entity
        if commit:
            instance.save()
        return instance  
    

class RepairProducerForm(ModelForm):
    class Meta:
        model = RepairProcedure
        exclude = ['reference_entity'] 
        fields = '__all__'
        widgets = {
            'configuration': forms.Textarea(attrs={'rows': 7, 'cols': 20}),
        } 

    def save(self, commit=True):
        instance = super().save(commit=False)
        reference_entity = ReferenceEntity.objects.get(name="Способ восстановления")
        instance.reference_entity = reference_entity
        if commit:
            instance.save()
        return instance  
    
class FailureUnitForm(ModelForm):
    class Meta:
        model = FailureUnit 
        exclude = ['reference_entity']      
        fields = '__all__'  
        widgets = {
            'configuration': forms.Textarea(attrs={'rows': 7, 'cols': 20}),
        }                              

    def save(self, commit=True):
        instance = super().save(commit=False)
        reference_entity = ReferenceEntity.objects.get(name="Узел отказа")
        instance.reference_entity = reference_entity
        if commit:
            instance.save()
        return instance      
    

class ReferenceCreateForm(ModelForm):
    class Meta:
        model = ReferenceEntity
        fields = '__all__'    