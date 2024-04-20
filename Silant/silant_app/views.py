from django.views.generic import ListView
from .models import Machine

class MachineListView(ListView):
    model = Machine
    template_name = 'index.html'
    context_object_name = 'machines'
    ordering = ['shipment_date']  # Сортировка по дате отгрузки с завода

    def get_queryset(self):
        queryset = super().get_queryset()
        # Фильтрация по дате отгрузки с завода (для примера, фильтрация по дате больше 2020-01-01)
        queryset = queryset.filter(shipment_date__gte='2020-01-01')
        return queryset