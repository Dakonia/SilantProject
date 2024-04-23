from django.views.generic import ListView, DetailView
from .models import *
from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


class MachineListView(ListView):
    model = Machine
    template_name = 'index.html'
    context_object_name = 'machines'
    ordering = ['shipment_date']  # Сортировка по дате отгрузки с завода

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return queryset
        elif user.groups.filter(name='Service').exists():
            return queryset.filter(service_department=user.servicedepartment)
        elif user.groups.filter(name='Client').exists():
            return queryset.filter(client=user.client)
        else:
            return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        serial_number = self.request.GET.get('serial-number')
        machines = context.get('machines')  # Получаем машины из контекста
        if serial_number:
            queryset = machines.filter(serial_number__icontains=serial_number)
            if queryset.exists():
                context['machines'] = queryset
                context['search_message'] = ''
            else:
                context['machines'] = None
                context['search_message'] = f'Машина с номером "{serial_number}" не найдена.'
            context['search_header'] = 'Результат поиска:'
        return context
    

  
class MaintenanceListView(ListView):
    model = Maintenance
    template_name = 'maintenance_list.html'
    context_object_name = 'maintenances'
    ordering = ['-maintenance_date']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return queryset
        elif user.groups.filter(name='Service').exists():
            return queryset.filter(service_department=user.servicedepartment)
        elif user.groups.filter(name='Client').exists():
            return queryset.filter(machine__client=user.client)
        else:
            return Maintenance.objects.none()
        
class MaintenanceDetailView(DetailView):
    model = Maintenance
    template_name = 'maintenance_detail.html'  
    context_object_name = 'maintenance'        
        

class ReclamationListView(ListView):
    model = Reclamation
    template_name = 'reclamation_list.html'
    context_object_name = 'reclamations'
    ordering = ['-failure_date']   


    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if user.is_authenticated:
            if user.groups.filter(name='Manager').exists():
                return queryset
            elif user.groups.filter(name='Service').exists():
                return queryset.filter(service_department=user.servicedepartment)
            elif user.groups.filter(name='Client').exists():
                return queryset.filter(machine__client=user.client)
        # Если пользователь не принадлежит ни к одной группе или не аутентифицирован, возвращаем пустой QuerySet
        return queryset.none()      




def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('machine-list')  # Перенаправление на главную страницу
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('/')

class MachineDetailView(DetailView):
    model = Machine
    template_name = 'Detail/machine_detail.html'
    context_object_name = 'machine'



class MaintenanceDetailView(DetailView):
    model = Maintenance
    template_name = 'maintenance_detail.html'
    context_object_name = 'maintenance'    


class MachineDetailView(DetailView):
    model = Machine
    template_name = 'machine_detail.html'
    context_object_name = 'machine'


class ReclamationDetailView(DetailView):
    model = Reclamation
    template_name = 'reclamation_detail.html'
    context_object_name = 'reclamation'


class MachineModelDetailView(DetailView):
    model = MachineModel
    template_name = 'machinemodel_detail.html'
    context_object_name = 'machinemodel'


class EngineModelDetailView(DetailView):
    model = EngineModel
    template_name = 'enginemodel_detail.html'
    context_object_name = 'enginemodel'

class TransmissionModelDetailView(DetailView):
    model = TransmissionModel
    template_name = 'transmissionmodel_detail.html'
    context_object_name = 'transmissionmodel'

class DriveAxleModelDetailView(DetailView):
    model = DriveAxleModel
    template_name = 'driveaxlemodel_detail.html'
    context_object_name = 'driveaxlemodel'


class SteerAxleModelDetailView(DetailView):
    model = SteerAxleModel
    template_name = 'steeraxlemodel_detail.html'
    context_object_name = 'steeraxlemodel'


class MaintenanceTypeModelDetailView(DetailView):
    model = MaintenanceType
    template_name = 'maintenancetype_detail.html'
    context_object_name = 'maintenancetype'


class ServiceDepartmentDetailView(DetailView):
    model = ServiceDepartment
    template_name = 'servicedepartament_detail.html'
    context_object_name = 'servicedepartementmodel'


class ServiceTODetailView(DetailView):
    model = ServiceTO
    template_name = 'serviceto_detail.html'
    context_object_name = 'servicetomodel'


    
               