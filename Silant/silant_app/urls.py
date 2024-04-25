# urls.py
from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', MachineListView.as_view(), name='machine-list'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'), 
    path('machine/<int:pk>/', MachineDetailView.as_view(), name='machine-detail'),
    path('machine/create/', MachineCreateView.as_view(), name='machine-create'),
    path('machinemodel/<int:pk>/', MachineModelDetailView.as_view(), name='model-detail'),
    path('enginemodel/<int:pk>/',EngineModelDetailView.as_view(),name='engine-detail'),
    path('transmission/<int:pk>/', TransmissionModelDetailView.as_view(), name='transmission'),
    path('driveaxle/<int:pk>/', DriveAxleModelDetailView.as_view(), name='drive-axle'),
    path('steeraxle/<int:pk>/', SteerAxleModelDetailView.as_view(), name='steer-axle'),
    path('maintenance/', MaintenanceListView.as_view(), name='maintenance-list'),
    path('reclamation/', ReclamationListView.as_view(), name='reclamation-list'),
    path('maintenancetype/<int:pk>/', MaintenanceTypeModelDetailView.as_view(), name='typeto'),
    path('servicedepartament/<int:pk>/', ServiceDepartmentDetailView.as_view(), name='service-dep'),
    path('serviceto/<int:pk>/', ServiceTODetailView.as_view(), name='service-to'),
    path('maintenance/<int:pk>/', MaintenanceDetailView.as_view(), name='maintenance-detail'),
    path('repairprocedure/<int:pk>/', RepairProcedureDetailView.as_view(), name='repairprocedure'),
    path('failureunit/<int:pk>/', FailureUnitDetailView.as_view(),name='failureunit'),
    path('reclamation/<int:pk>/', ReclamationDetailView.as_view(), name='reclamation-detail'),
    path('reclamation/', ReclamationListView.as_view(), name='reclamation-list'),
    path('maintenance/create/', MaintenanceCreateView.as_view(), name='maintenance-create'),
    path('reclamation/create/', ReclamationCreateView.as_view(), name='reclamation-create'),
]