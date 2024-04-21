from django.views.generic import ListView
from .models import *
from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import authenticate, login, logout

class MachineListView(ListView):
    model = Machine
    template_name = 'index.html'
    context_object_name = 'machines'
    ordering = ['shipment_date']  # Сортировка по дате отгрузки с завода

    def get_queryset(self):
        queryset = super().get_queryset()
        serial_number = self.request.GET.get('serial-number')
        if serial_number:
            queryset = queryset.filter(serial_number=serial_number)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        serial_number = self.request.GET.get('serial-number')
        if serial_number:
            if context['machines']:
                context['search_message'] = f''
            else:
                context['search_message'] = f'Данная машина с номером "{serial_number}" не найдена.'
            context['search_header'] = 'Результат поиска:'
        return context
    

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