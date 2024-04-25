from django.views.generic import ListView, DetailView, CreateView
from .models import *
from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy


class MachineListView(ListView):
    model = Machine
    template_name = 'index.html'
    context_object_name = 'machines'
    ordering = ['shipment_date']  # Сортировка по дате отгрузки с завода

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-shipment_date')

        # Фильтрация по номеру машины
        serial_number = self.request.GET.get('serial-number')
        if serial_number:
            queryset = queryset.filter(serial_number__icontains=serial_number)

        # Фильтрация по моделям
        model_id = self.request.GET.get('model')
        engine_id = self.request.GET.get('engine')
        transmission_id = self.request.GET.get('transmission')
        drive_axle_id = self.request.GET.get('drive_axle')
        steer_axle_id = self.request.GET.get('steer_axle')

        if model_id:
            queryset = queryset.filter(model_id=model_id)
        if engine_id:
            queryset = queryset.filter(engine_model_id=engine_id)
        if transmission_id:
            queryset = queryset.filter(transmission_model_id=transmission_id)
        if drive_axle_id:
            queryset = queryset.filter(drive_axle_model_id=drive_axle_id)
        if steer_axle_id:
            queryset = queryset.filter(steer_axle_model_id=steer_axle_id)

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
        user = self.request.user

        # Инициализация переменных
        machine_models = None
        engine_models = None
        transmission_models = None
        drive_axle_models = None
        steer_axle_models = None

        if user.is_authenticated:
            if user.groups.filter(name='Manager').exists():
                machine_models = MachineModel.objects.all()
                engine_models = EngineModel.objects.all()
                transmission_models = TransmissionModel.objects.all()
                drive_axle_models = DriveAxleModel.objects.all()
                steer_axle_models = SteerAxleModel.objects.all()
            
            elif user.groups.filter(name='Service').exists():
                service_department = user.servicedepartment
                service_department_machines = Machine.objects.filter(service_department=service_department)
                engine_models = EngineModel.objects.filter(machine__in=service_department_machines).distinct()
                transmission_models = TransmissionModel.objects.filter(machine__in=service_department_machines).distinct()
                drive_axle_models = DriveAxleModel.objects.filter(machine__in=service_department_machines).distinct()
                steer_axle_models = SteerAxleModel.objects.filter(machine__in=service_department_machines).distinct()
                machine_models = MachineModel.objects.filter(id__in=service_department_machines.values_list('model_id', flat=True)).distinct()


            elif user.groups.filter(name='Client').exists():
                client = user.client
                machine_models = MachineModel.objects.filter(machine__client=client).distinct()
                engine_models = EngineModel.objects.filter(machine__client=client).distinct()
                transmission_models = TransmissionModel.objects.filter(machine__client=client).distinct()
                drive_axle_models = DriveAxleModel.objects.filter(machine__client=client).distinct()
                steer_axle_models = SteerAxleModel.objects.filter(machine__client=client).distinct()

        # Передаем модели в контекст
        context['machine_models'] = machine_models
        context['engine_models'] = engine_models
        context['transmission_models'] = transmission_models
        context['drive_axle_models'] = drive_axle_models
        context['steer_axle_models'] = steer_axle_models

        if not context['machines']:
            context['search_message'] = "Данная машина не найдена"

        return context
    
class MachineCreateView(CreateView):
    model = Machine
    form_class = MachineForm
    template_name = 'machine_create.html'
    success_url = reverse_lazy('machine-list')    
 

class MaintenanceListView(ListView):
    model = Maintenance
    template_name = 'maintenance_list.html'
    context_object_name = 'maintenances'
    ordering = ['-maintenance_date']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Фильтрация по полям
        maintenance_type_id = self.request.GET.get('maintenance-type')
        maintenance_service_id = self.request.GET.get('maintenance-service')
        serial_number = self.request.GET.get('serial-number')

        if maintenance_type_id:
            queryset = queryset.filter(maintenance_type_id=maintenance_type_id)
        if maintenance_service_id:
            queryset = queryset.filter(maintenance_service_id=maintenance_service_id)
        if serial_number:
            queryset = queryset.filter(machine__serial_number__icontains=serial_number)

        # Применение фильтров для разных типов пользователей
        if user.groups.filter(name='Manager').exists():
            return queryset
        elif user.groups.filter(name='Service').exists():
            # Проверяем, есть ли у пользователя ссылка на сервисное подразделение
            if hasattr(user, 'servicedepartment'):
                return queryset.filter(service_department=user.servicedepartment)
            else:
                # Если у пользователя нет ссылки на сервисное подразделение, вернуть пустой queryset
                return Maintenance.objects.none()
        elif user.groups.filter(name='Client').exists():
            return queryset.filter(machine__client=user.client)
        else:
            return Maintenance.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Инициализация переменных
        maintenance_types = None
        maintenance_services = None
        service_departments = None

        if user.is_authenticated:
            if user.groups.filter(name='Manager').exists():
                maintenance_types = MaintenanceType.objects.all()
                maintenance_services = ServiceTO.objects.all()
                service_departments = ServiceDepartment.objects.all()

            elif user.groups.filter(name='Service').exists():
                service_department = user.servicedepartment
                machines = Machine.objects.filter(service_department=service_department)
                maintenance_types = MaintenanceType.objects.filter(maintenance__machine__in=machines).distinct()
                maintenance_services = ServiceTO.objects.filter(maintenance__machine__in=machines).distinct()
                service_departments = ServiceDepartment.objects.filter(id=service_department.id)

            elif user.groups.filter(name='Client').exists():
                client = user.client
                client_machines = Machine.objects.filter(client=client)
                maintenance_services = ServiceTO.objects.filter(maintenance__machine__in=client_machines).distinct()
                maintenance_types = MaintenanceType.objects.filter(maintenance__machine__in=client_machines).distinct()
                service_departments = ServiceDepartment.objects.filter(maintenance__machine__in=client_machines).distinct()

    

        # Передача значений в контекст
        context['maintenance_types'] = maintenance_types
        context['maintenance_services'] = maintenance_services
        context['service_departments'] = service_departments

        if not context['maintenances']:
            context['search_message'] = "Данное ТО не найдено"


        return context


class MaintenanceCreateView(CreateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = 'maintenance_create.html'
    success_url = reverse_lazy('maintenance-list')        
  
        
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
        serial_number = self.request.GET.get('serial-number')

        if serial_number:
            queryset = queryset.filter(machine__serial_number__icontains=serial_number)

        if user.is_authenticated:
            if user.groups.filter(name='Manager').exists():
                return queryset
            elif user.groups.filter(name='Service').exists():
                return queryset.filter(service_department=user.servicedepartment)
            elif user.groups.filter(name='Client').exists():
                return queryset.filter(machine__client=user.client)
        return queryset.none()  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Инициализация переменных
        failure_units = None
        repair_procedures = None
        service_departments = None

        if user.is_authenticated:
            if user.groups.filter(name='Manager').exists():
                failure_units = FailureUnit.objects.all()
                repair_procedures = RepairProcedure.objects.all()
                service_departments = ServiceDepartment.objects.all()

            elif user.groups.filter(name='Service').exists():
                service_department = user.servicedepartment
                machines = Machine.objects.filter(service_department=service_department)
                failure_units = FailureUnit.objects.filter(reclamation__machine__in=machines).distinct()
                repair_procedures = RepairProcedure.objects.filter(reclamation__machine__in=machines).distinct()
                service_departments = ServiceDepartment.objects.filter(id=service_department.id)

            elif user.groups.filter(name='Client').exists():
                client = user.client
                client_machines = Machine.objects.filter(client=client)
                failure_units = FailureUnit.objects.filter(reclamation__machine__in=client_machines).distinct()
                repair_procedures = RepairProcedure.objects.filter(reclamation__machine__in=client_machines).distinct()
                service_departments = ServiceDepartment.objects.filter(reclamation__machine__in=client_machines).distinct()

        # Передача значений в контекст
        context['failure_units'] = failure_units
        context['repair_procedures'] = repair_procedures
        context['service_departments'] = service_departments

        if not context['reclamations']:
            context['search_message'] = "Данная рекламация не найдена"


        return context    

class ReclamationCreateView(CreateView):
    model = Reclamation
    form_class = ReclamationForm
    template_name = 'reclamation_create.html'
    success_url = reverse_lazy('reclamation-list')


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


class RepairProcedureDetailView(DetailView):
    model = RepairProcedure
    template_name = 'repairprocedure_detail.html'
    context_object_name = 'repairprocedure'


class FailureUnitDetailView(DetailView):
    model = FailureUnit
    template_name = 'failureunit_detail.html'
    context_object_name = 'failureunit'    

    
               