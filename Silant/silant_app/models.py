from django.db import models
from django.contrib.auth.models import User

class ReferenceEntity(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название справочника")
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.name

class MachineModel(models.Model):
    reference_entity = models.ForeignKey(ReferenceEntity, on_delete=models.CASCADE, verbose_name="Название справочника")
    name = models.CharField(max_length=255, verbose_name="Модель техники")
    description = models.TextField(verbose_name="Описание ")

    def __str__(self):
        return self.name
    
class EngineModel(models.Model):
    reference_entity = models.ForeignKey(ReferenceEntity, on_delete=models.CASCADE, verbose_name="Название справочника")
    name = models.CharField(max_length=255, verbose_name="Модель двигателя")
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.name

class TransmissionModel(models.Model):
    reference_entity = models.ForeignKey(ReferenceEntity, on_delete=models.CASCADE, verbose_name="Название справочника")
    name = models.CharField(max_length=255, verbose_name="Модель трансмиссии")
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.name

class DriveAxleModel(models.Model):
    reference_entity = models.ForeignKey(ReferenceEntity, on_delete=models.CASCADE, verbose_name="Название справочника")
    name = models.CharField(max_length=255, verbose_name="Модель ведущего моста")
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.name

class SteerAxleModel(models.Model):
    reference_entity = models.ForeignKey(ReferenceEntity, on_delete=models.CASCADE, verbose_name="Название справочника")
    name = models.CharField(max_length=255, verbose_name="Модель управляемого моста")
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.name

class MaintenanceType(models.Model):
    reference_entity = models.ForeignKey(ReferenceEntity, on_delete=models.CASCADE, verbose_name="Название справочника")
    name = models.CharField(max_length=255, verbose_name="Вид ТО")
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.name

class FailureUnit(models.Model):
    reference_entity = models.ForeignKey(ReferenceEntity, on_delete=models.CASCADE, verbose_name="Название справочника")
    name = models.CharField(max_length=255, verbose_name="Узел отказа")
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.name

class RepairProcedure(models.Model):
    reference_entity = models.ForeignKey(ReferenceEntity, on_delete=models.CASCADE, verbose_name="Название справочника")
    name = models.CharField(max_length=255, verbose_name="Способ восстановления")
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.name

class ServiceDepartment(models.Model):
    reference_entity = models.ForeignKey(ReferenceEntity, on_delete=models.CASCADE, verbose_name="Название справочника")
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(max_length=255, default="Сервисная компания", verbose_name="Описание")
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")

    def __str__(self):
        return self.name   

class ServiceTO(models.Model):
    reference_entity = models.ForeignKey(ReferenceEntity, on_delete=models.CASCADE, verbose_name="Название справочника")
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(max_length=255, default="Организация, проводившая ТО", verbose_name="Описание")

    def __str__(self):
        return self.name         


class Client(models.Model):
    reference_entity = models.ForeignKey(ReferenceEntity, on_delete=models.CASCADE, verbose_name="Название справочника")
    name = models.CharField(max_length=255, verbose_name="Имя клиента")
    description = models.TextField(max_length=255, default="Клиент", verbose_name="Описание")
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")

    def __str__(self):
        return self.name  

class Machine(models.Model):
    reference_entity = models.ForeignKey(ReferenceEntity, on_delete=models.CASCADE, verbose_name="Название")
    model = models.ForeignKey(MachineModel, on_delete=models.CASCADE, verbose_name="Модель техники")
    serial_number = models.CharField(unique=True, max_length=255, verbose_name="Заводской № машины")
    engine_model = models.ForeignKey(EngineModel, on_delete=models.CASCADE, verbose_name="Модель двигателя")
    engine_serial_number = models.CharField(unique=True, max_length=255, verbose_name="Заводской № двигателя")
    transmission_model = models.ForeignKey(TransmissionModel, on_delete=models.CASCADE, verbose_name="Модель трансмиссии")
    transmission_serial_number = models.CharField(unique=True, max_length=255, verbose_name="Заводской № трансмиссии")
    drive_axle_model = models.ForeignKey(DriveAxleModel, on_delete=models.CASCADE, verbose_name="Модель ведущего моста")
    drive_axle_serial_number = models.CharField(max_length=255, verbose_name="Заводской № ведущего моста")
    steer_axle_model = models.ForeignKey(SteerAxleModel, on_delete=models.CASCADE, verbose_name="Модель управляемого моста")
    steer_axle_serial_number = models.CharField(max_length=255, verbose_name="Заводской № управляемого моста")
    delivery_contract = models.CharField(max_length=255, verbose_name="Договор поставки (№, дата)")
    shipment_date = models.DateField(verbose_name="Дата отгрузки с завода")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент")
    end_user = models.CharField(max_length=255, verbose_name="Грузополучатель (конечный потребитель)")
    shipping_address = models.CharField(max_length=255, verbose_name="Адрес поставки (эксплуатации)")
    configuration = models.TextField(max_length=1000, default="Стандарт", verbose_name="Комплектация (доп. опции)")
    service_department = models.ForeignKey(ServiceDepartment, on_delete=models.CASCADE, verbose_name="Сервисная компания")

    def __str__(self):
        return self.serial_number           
    

class Maintenance(models.Model):
    reference_entity = models.ForeignKey(ReferenceEntity, on_delete=models.CASCADE, verbose_name="Название справочника")
    maintenance_type = models.ForeignKey(MaintenanceType, on_delete=models.CASCADE, verbose_name="Вид ТО")
    maintenance_date = models.DateField(verbose_name="Дата проведения ТО")
    operating_time = models.IntegerField(default=0, verbose_name="Наработка, м/час")
    order_number = models.CharField(max_length=255, verbose_name="Номер заказ-наряда")
    order_date = models.DateField(verbose_name="Дата заказ-наряда")
    maintenance_service = models.ForeignKey(ServiceTO, on_delete=models.CASCADE, verbose_name="Организация, проводившая ТО")
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, verbose_name="Машина")
    service_department = models.ForeignKey(ServiceDepartment, on_delete=models.CASCADE, verbose_name="Сервисная компания")

    def __str__(self):
        return f"{self.machine} - {self.maintenance_type} - {self.maintenance_date}"

class Reclamation(models.Model):
    reference_entity = models.ForeignKey(ReferenceEntity, on_delete=models.CASCADE, verbose_name="Название справочника")
    failure_date = models.DateField(verbose_name="Дата отказа")
    operating_time = models.IntegerField(default=0, verbose_name="Наработка, м/час")
    failure_unit = models.ForeignKey(FailureUnit, on_delete=models.CASCADE, verbose_name="Узел отказа")
    failure_description = models.TextField(max_length=1000, verbose_name="Описание отказа")
    repair_procedure = models.ForeignKey(RepairProcedure, on_delete=models.CASCADE, verbose_name="Способ восстановления")
    spare_parts = models.TextField(max_length=1000, blank=True, verbose_name="Используемые запасные части")
    repair_date = models.DateField(verbose_name="Дата восстановления")
    nonuse_time = models.IntegerField(default=0, verbose_name="Время простоя техники")
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, verbose_name="Машина")
    service_department = models.ForeignKey(ServiceDepartment, on_delete=models.CASCADE, verbose_name="Сервисная компания")

    def save(self, *args, **kwargs):
        self.nonuse_time = (self.repair_date - self.failure_date).days
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.machine} - {self.failure_date} - {self.failure_unit}"
