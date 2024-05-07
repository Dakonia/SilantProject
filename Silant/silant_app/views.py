from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import *
from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from .serializers import *
from rest_framework import generics





class MachineListView(ListView):
    model = Machine
    template_name = 'index.html'
    context_object_name = 'machines'
    ordering = ['shipment_date'] 
    paginate_by = 15

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
        if user.is_superuser or user.groups.filter(name='Manager').exists():
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
            if user.is_superuser or user.groups.filter(name='Manager').exists():
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

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 



def error_view(request):
    return render(request, 'error.html')    



class MachineDetailView(DetailView):
    model = Machine
    template_name = 'machine_detail.html'
    context_object_name = 'machine'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs)

class MaintenanceListView(ListView):
    model = Maintenance
    template_name = 'maintenance_list.html'
    context_object_name = 'maintenances'
    ordering = ['-maintenance_date']
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-maintenance_date')
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
        if user.is_superuser or user.groups.filter(name='Manager').exists():
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
            if user.is_superuser or user.groups.filter(name='Manager').exists():
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
    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs)

class MaintenanceEditView(UpdateView):
    model = Maintenance
    form_class = MaintenanceFormEdit
    template_name = 'maintenance_edit.html'  
    success_url = reverse_lazy('maintenance-list')  

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs)  


class MaintenanceCreateView(CreateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = 'maintenance_create.html'
    success_url = reverse_lazy('maintenance-list') 

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs



    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs)       
  
        
class MaintenanceDetailView(DetailView):
    model = Maintenance
    template_name = 'maintenance_detail.html'  
    context_object_name = 'maintenance'  

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs)


class MachineEditView(UpdateView):
    model = Machine
    form_class = MachineFormEdit
    template_name = 'machine_edit.html'  
    success_url = reverse_lazy('machine-list')

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 


class MachineDeleteView(DeleteView):
    model = Machine
    success_url = reverse_lazy('machine-list')
    template_name = 'machine_delete.html' 

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs)     


class MaintenanceDeleteView(DeleteView):
    model = Maintenance 
    success_url = reverse_lazy('maintenance-list')
    template_name = 'maintenance_delete.html' 

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs)
        

class ReclamationListView(ListView):
    model = Reclamation
    template_name = 'reclamation_list.html'
    context_object_name = 'reclamations'
    ordering = ['-failure_date']
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-failure_date')
        user = self.request.user
        serial_number = self.request.GET.get('serial-number')
        failure_unit_id = self.request.GET.get('failure-unit')
        repair_procedure_id = self.request.GET.get('repair-procedure')
        service_department_id = self.request.GET.get('service-department')

        if serial_number:
            queryset = queryset.filter(machine__serial_number__icontains=serial_number)

        if failure_unit_id:
            queryset = queryset.filter(failure_unit=failure_unit_id)

        if repair_procedure_id:
            queryset = queryset.filter(repair_procedure=repair_procedure_id)

        if service_department_id:
            queryset = queryset.filter(service_department=service_department_id)

        if user.is_authenticated:
            if user.is_superuser or user.groups.filter(name='Manager').exists():
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
            if user.is_superuser or user.groups.filter(name='Manager').exists():
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
        print("Failure Units:", failure_units)
        print("Repair Procedures:", repair_procedures)
        print("Service Departments:", service_departments)

        if not context['reclamations']:
            context['search_message'] = "Данная рекламация не найдена"

        return context

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs)
     

class ReclamationCreateView(CreateView):
    model = Reclamation
    form_class = ReclamationForm
    template_name = 'reclamation_create.html'
    success_url = reverse_lazy('reclamation-list')

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs)


class REclamationEditView(UpdateView):
    model = Reclamation
    form_class = ReclamationFormEdit
    template_name = 'reclamation_edit.html'  
    success_url = reverse_lazy('reclamation-list') 

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs) 


class ReclamationDeleteView(DeleteView):
    model = Reclamation  
    success_url = reverse_lazy('reclamation-list')
    template_name = 'reclamation-delete.html' 

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs)     


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('machine-list')  
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


    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs)




class ReclamationDetailView(DetailView):
    model = Reclamation
    template_name = 'reclamation_detail.html'
    context_object_name = 'reclamation'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs)


class MachineModelDetailView(DetailView):
    model = MachineModel
    template_name = 'machinemodel_detail.html'
    context_object_name = 'machinemodel'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs)


class EngineModelDetailView(DetailView):
    model = EngineModel
    template_name = 'enginemodel_detail.html'
    context_object_name = 'enginemodel'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs)

class TransmissionModelDetailView(DetailView):
    model = TransmissionModel
    template_name = 'transmissionmodel_detail.html'
    context_object_name = 'transmissionmodel'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs)

class DriveAxleModelDetailView(DetailView):
    model = DriveAxleModel
    template_name = 'driveaxlemodel_detail.html'
    context_object_name = 'driveaxlemodel'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs)


class SteerAxleModelDetailView(DetailView):
    model = SteerAxleModel
    template_name = 'steeraxlemodel_detail.html'
    context_object_name = 'steeraxlemodel'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs)


class MaintenanceTypeModelDetailView(DetailView):
    model = MaintenanceType
    template_name = 'maintenancetype_detail.html'
    context_object_name = 'maintenancetype'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs)


class ServiceDepartmentDetailView(DetailView):
    model = ServiceDepartment
    template_name = 'servicedepartament_detail.html'
    context_object_name = 'servicedepartementmodel'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs)



class ServiceTODetailView(DetailView):
    model = ServiceTO
    template_name = 'serviceto_detail.html'
    context_object_name = 'servicetomodel'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs)


class RepairProcedureDetailView(DetailView):
    model = RepairProcedure
    template_name = 'repairprocedure_detail.html'
    context_object_name = 'repairprocedure'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs)


class FailureUnitDetailView(DetailView):
    model = FailureUnit
    template_name = 'failureunit_detail.html'
    context_object_name = 'failureunit'  

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Manager', 'Service', 'Client']).exists() and not self.request.user.is_superuser:
            return redirect('error')
        return super().dispatch(*args, **kwargs)  

    
class ReferenceEntityViews(ListView):
    model = ReferenceEntity
    template_name = 'reference/reference-list.html'
    context_object_name = "reference"

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 


class ReferenceEntityDetail(DeleteView):
    model = ReferenceEntity
    template_name = 'reference/reference_detail.html'
    context_object_name = 'reference'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

class EngineModelCreate(CreateView):    
    model = EngineModel
    form_class = EngineForm
    template_name = 'engine_create.html'
    context_object_name = 'create-engine'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id})

class EngineModelUpdate(UpdateView):
    model = EngineModel
    template_name = 'engine-edit.html'
    form_class = EngineForm
    context_object_name = 'engine-edit'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id})   


class EngineModelDelete(DeleteView):
    model = EngineModel
    template_name = 'engine_delete.html'
    context_object_name = 'engine-delete'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs)  

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id}) 

class MachineModelCreate(CreateView):
    model = MachineModel
    template_name = 'machine_model_create.html'
    form_class = MachineModelFrom
    context_object_name = 'machinemodel-create'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 


    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id})
    
class MachineModelUpdate(UpdateView):
    model = MachineModel
    template_name = 'machinemodel_edit.html'
    form_class = MachineModelFrom
    context_object_name = 'machinemodel-edit'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id})
    
class MachineModelDelete(DeleteView):
    model = MachineModel
    template_name = 'machinemodel_delete.html'
    context_object_name = 'machinemodel-delete'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id})
    

class TransmissionModelCreate(CreateView):
    model = TransmissionModel
    template_name = 'transmission_create.html'
    context_object_name = 'transmission-create'
    form_class = TransmissionForm

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id})
    

class TransmissiomModelUpdate(UpdateView):
    model = TransmissionModel
    template_name = 'transmission_edit.html'
    context_object_name ='transmissiom-edit'
    form_class =TransmissionForm

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id})
    

class TranssmissionModelDelete(DeleteView):
    model = TransmissionModel
    template_name = 'transsmision_delete.html'
    context_object_name ='transmission-delete'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id})
    
class DriveAxleCreate(CreateView):
    model = DriveAxleModel
    template_name = 'driveaxle_create.html'
    context_object_name = 'driveaxle-create'
    form_class = DriveAxleForm

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id})


class DriveAxleUpdate(UpdateView):
    model = DriveAxleModel
    template_name = 'driveaxle_edit.html'
    form_class = DriveAxleForm
    context_object_name = 'dirveasxle-edit'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id})

class DriveAxleDelete(DeleteView):
    model = DriveAxleModel
    template_name = 'driveaxle_delete.html'
    context_object_name = 'driveaxle-delete'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id})   


class SteerAxleCreate(CreateView):
    model = SteerAxleModel
    template_name = 'steeraxle_create.html'
    context_object_name = 'steeraxle-create'
    form_class = SteerAxleForm

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id}) 


class SteerAxleUpdate(UpdateView):
    model = SteerAxleModel
    template_name = 'steeraxle_edit.html'
    context_object_name = 'steeraxle-edit'
    form_class = SteerAxleForm 

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id}) 


class SteerAxleDelete(DeleteView):
    model = SteerAxleModel
    template_name = 'steeraxle_delete.html'
    context_object_name ='steeraxle-delete'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id}) 
    

class MaintenanceTypeCreate(CreateView):
    model = MaintenanceType
    template_name = 'maintenancetype_create.html'
    context_object_name = 'maintenancetype-create'
    form_class = MaintenanceTypeForm

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id})


class MaintenanceTypeUpdate(UpdateView):
    model = MaintenanceType
    template_name = 'maintenancetype_edit.html'
    context_object_name ='maintenancetype-edit'
    form_class = MaintenanceTypeForm 

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id})       


class MaintenanceTypeDelete(DeleteView):
    model = MaintenanceType
    template_name = 'maintenancetype_delete.html'
    context_object_name = 'maintenancetype-edit'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id})  
    

class ServiceToCreate(CreateView):
    model = ServiceTO
    template_name = 'serviceto_create.html'
    context_object_name = 'serviceto-create'  
    form_class =ServiceToForm

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id}) 


class ServiceToUpdate(UpdateView):
    model = ServiceTO
    template_name = 'serviceto_edit.html'
    form_class = ServiceToForm 
    context_object_name = 'serviceto-edit'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id}) 


class ServiceToDelete(DeleteView):
    model = ServiceTO
    template_name = 'serviceto_delete.html'
    context_object_name ='serviceto-delete' 

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs)         


    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id}) 
    


class RepairProcedureCreate(CreateView):
    model = RepairProcedure
    template_name = 'repair_create.html'
    form_class = RepairProducerForm
    context_object_name = 'repair-create'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id})



class RepairProducerEdit(UpdateView):
    model = RepairProcedure 
    template_name = 'repair_edit.html'
    form_class = RepairProducerForm
    context_object_name = 'repair-edit'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id})


class RepairProducerDelete(DeleteView):
    model = RepairProcedure
    template_name = 'repair_delete.html' 
    context_object_name = 'repair-delete'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id})          



class FailureUnitCreate(CreateView):
    model = FailureUnit
    template_name = 'faile_create.html'
    context_object_name = 'faile-create'
    form_class = FailureUnitForm

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id}) 

class FailureUnitEdit(UpdateView):
    model = FailureUnit
    template_name = 'faile_edit.html'
    context_object_name = 'faile-edit'
    form_class = FailureUnitForm

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id}) 


class FailureUnitDelete(DeleteView):
    model = FailureUnit 
    template_name = 'faile_delete.html'
    context_object_name = 'daile-delete'   

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Manager').exists() or u.is_superuser))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            # Если пользователь не является менеджером, перенаправляем на страницу ошибки
            return redirect('error')
        return super().dispatch(*args, **kwargs) 

    def get_success_url(self):
        reference_entity_id = self.object.reference_entity.pk
        return reverse_lazy('reference-detail', kwargs={'pk': reference_entity_id})     


class MachineList(generics.ListAPIView):
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer

class MachineDetail(generics.RetrieveAPIView):
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer

class MaintenanceList(generics.ListAPIView):
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer

class MaintenanceDetail(generics.RetrieveAPIView):
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer

class ReclamationList(generics.ListAPIView):
    queryset = Reclamation.objects.all()
    serializer_class = ReclamationSerializer

class ReclamationDetail(generics.RetrieveAPIView):
    queryset = Reclamation.objects.all()
    serializer_class = ReclamationSerializer

class ReferenceEntityCreate(CreateView):
    model= ReferenceEntity
    template_name = 'reference/reference_create.html'
    context_object_name = 'reference-create'
    form_class = ReferenceCreateForm
    success_url = reverse_lazy('reference-list')


