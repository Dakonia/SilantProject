from django.contrib import admin
from .models import *

admin.site.register(ReferenceEntity)
admin.site.register(MachineModel)
admin.site.register(EngineModel)
admin.site.register(TransmissionModel)
admin.site.register(DriveAxleModel)
admin.site.register(SteerAxleModel)
admin.site.register(MaintenanceType)
admin.site.register(FailureUnit)
admin.site.register(RepairProcedure)
admin.site.register(ServiceDepartment)
admin.site.register(ServiceTO)
admin.site.register(Client)

class MachineAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name='Manager').exists():
            return qs
        elif hasattr(request.user, 'client'):
            return qs.filter(client__user=request.user)
        elif hasattr(request.user, 'servicedepartment'):
            return qs.filter(service_department__user=request.user)

admin.site.register(Machine, MachineAdmin)

class MaintenanceAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name='Manager').exists():
            return qs
        # Фильтруем ТО по машинам, связанным с профилем клиента или сервисной организации
        if hasattr(request.user, 'client'):
            return qs.filter(machine__client__user=request.user)
        elif hasattr(request.user, 'servicedepartment'):
            return qs.filter(machine__service_department__user=request.user)

admin.site.register(Maintenance, MaintenanceAdmin)

class ReclamationAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name='Manager').exists():
            return qs
        # Фильтруем рекламации по машинам, связанным с профилем клиента или сервисной организации
        if hasattr(request.user, 'client'):
            return qs.filter(machine__client__user=request.user)
        elif hasattr(request.user, 'servicedepartment'):
            return qs.filter(machine__service_department__user=request.user)

admin.site.register(Reclamation, ReclamationAdmin)




