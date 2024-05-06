from django.shortcuts import render
from django.http import JsonResponse
from .models import Employee
from django.core.serializers import serialize


def main_view(request):
    return render(request, 'main.html')

def calendar_view(request):
    return render(request, 'calendar.html')

def orders_view(request):
    return render(request, 'orders.html')

def active_view(request):
    return render(request, 'active.html')

def staff_view(request):
    # Mapping dictionary for English keys and Russian values
    STATUS_CHOICES_MAPPING = {
        'working': 'Работает',
        'not_working': 'Не работает',
        'probation': 'Испытательный срок',
    }

    DEPARTMENT_CHOICES_MAPPING = {
        'office': 'Офис',
        'workshop': 'Цех',
    }

    SALARY_CHOICES_MAPPING = {
        'fixed': 'Фиксированный',
        'not_fixed': 'Не фиксированный',
    }

    employees = Employee.objects.all()

    search_name = request.GET.get('search_name', '')
    if search_name:
        employees = employees.filter(last_name__icontains=search_name)

    status = request.GET.get('status', '')
    if status:
        employees = employees.filter(status=status)

    department = request.GET.get('department', '')
    if department:
        employees = employees.filter(department=department)

    payment_type = request.GET.get('payment_type', '')
    if payment_type:
        employees = employees.filter(type_salary=payment_type)

    # Check for AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = list(employees.values(
            'last_name', 'first_name', 'middle_name', 'position',
            'department', 'employment_date', 'status', 'type_salary', 'salary'))

        # Convert the keys to Russian values
        for item in data:
            item['status'] = STATUS_CHOICES_MAPPING.get(item['status'], item['status'])
            item['department'] = DEPARTMENT_CHOICES_MAPPING.get(item['department'], item['department'])
            item['type_salary'] = SALARY_CHOICES_MAPPING.get(item['type_salary'], item['type_salary'])

        return JsonResponse({'data': data}, safe=False)

    return render(request, 'staff.html', {'employees': employees})
