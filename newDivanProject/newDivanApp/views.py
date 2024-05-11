from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import *
from .models import Order, TechnicalSpecification, Contract
from django.core.serializers import serialize
from .forms import (NameForm, AvatarForm, PositionForm, StatusForm, CitizenshipForm, PassportForm, SalaryForm)
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from decimal import Decimal
from datetime import datetime


def main_view(request):
    return render(request, 'main.html')

def calendar_view(request):
    return render(request, 'calendar.html')



def active_view(request):
    return render(request, 'active.html')








#ЗАКАЗЫ
def get_payment_status(contract, pickup_delivery):
    if not contract.is_prepayment_paid and not contract.is_postpayment_paid:
        return "Ожидает предоплаты"
    elif contract.is_prepayment_paid and not contract.is_postpayment_paid:
        if pickup_delivery and pickup_delivery.delivery_date:
            return "Ожидает оплаты"
        return "Внесена предоплата"
    elif contract.is_postpayment_paid:
        return "Оплата произведена"
    return "Неопределенный статус"

def orders_view(request):
    orders = Order.objects.select_related(
        'contract', 'manager', 'executor1', 'executor2', 'executor3'
    ).prefetch_related('technical_specifications', 'pickupdelivery_set')

    total_count = orders.count()

    # Получаем параметры фильтрации из GET-запроса
    search_query = request.GET.get('search_query', '')
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    payment_status_filter = request.GET.get('payment_status', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # Фильтрация по номеру заказа или описанию
    if search_query:
        orders = orders.filter(
            Q(number__icontains=search_query) |
            Q(technical_specifications__short_descr__icontains=search_query)
        ).distinct()

    # Фильтрация по статусу заказа
    if status_filter:
        orders = orders.filter(status=status_filter)

    # Фильтрация по типу мебели
    if type_filter:
        orders = orders.filter(technical_specifications__furniture_type1=type_filter)

    # Расширенная фильтрация по статусу оплаты
    if payment_status_filter:
        if payment_status_filter == "awaiting_prepayment":
            orders = orders.filter(contract__is_prepayment_paid=False, contract__is_postpayment_paid=False)
        elif payment_status_filter == "prepayment_made":
            orders = orders.filter(contract__is_prepayment_paid=True, contract__is_postpayment_paid=False, pickupdelivery_set__delivery_date__isnull=True)
        elif payment_status_filter == "awaiting_payment":
            orders = orders.filter(contract__is_prepayment_paid=True, contract__is_postpayment_paid=False, pickupdelivery_set__delivery_date__isnull=False)
        elif payment_status_filter == "payment_done":
            orders = orders.filter(contract__is_postpayment_paid=True)

    if start_date and end_date:
        orders = orders.filter(contract__create_date__range=[start_date, end_date])

    # AJAX запрос для обновления таблицы заказов без перезагрузки страницы
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = format_orders_data(orders)
        return JsonResponse({'data': data, 'total_count': total_count}, safe=False)

    return render(request, 'orders.html', {
        'orders': orders
    })

def format_orders_data(orders):
    data = []
    for order in orders:
        pickup_delivery = order.pickupdelivery_set.first()
        payment_status = get_payment_status(order.contract, pickup_delivery)

        # Список исполнителей
        executors = []
        for executor in [order.executor1, order.executor2, order.executor3]:
            if executor:
                executors.append({
                    'avatar_url': executor.avatar.url if executor.avatar else '',
                    'full_name': f"{executor.first_name} {executor.last_name}"
                })

        # Добавление информации о менеджере
        manager = {
            'full_name': f"{order.manager.first_name} {order.manager.last_name}" if order.manager else "Нет данных",
            'avatar_url': order.manager.avatar.url if order.manager and order.manager.avatar else ''
        }

        data.append({
            'number': order.number,
            'create_date': order.contract.create_date.strftime('%d.%m.%Y'),
            'completion_date': order.contract.completion_date.strftime('%d.%m.%Y'),
            'total_value': "{:,.2f}".format(order.contract.total_value).replace(",", " ").replace(".", ","),
            'type': order.technical_specifications.first().get_furniture_type1_display() if order.technical_specifications.exists() else '',
            'description': order.technical_specifications.first().short_descr if order.technical_specifications.exists() else '',
            'payment_status': payment_status,
            'status': order.get_status_display(),
            'executors': executors,
            'manager': manager  # Добавление информации о менеджере в вывод
        })
    return data


@csrf_exempt
def add_order(request):
    manager_position = JobTitle.objects.filter(name='Менеджер').first()
    managers = Employee.objects.filter(position=manager_position) if manager_position else Employee.objects.none()
    worker_position = JobTitle.objects.filter(name='Рабочий').first()
    executors = Employee.objects.filter(position=worker_position) if worker_position else Employee.objects.none()

    if request.method == 'POST':
        number = request.POST.get('number')
        manager_id = request.POST.get('manager')
        executors_ids = request.POST.getlist('executors')
        source = request.POST.get('source')
        contract_num = request.POST.get('contract_num')
        create_date = request.POST.get('create_date')
        completion_date = request.POST.get('completion_date')
        total_value = request.POST.get('total_value')
        payment_type = request.POST.get('payment_type')
        prepayment_share = request.POST.get('prepayment_share')
        prepayment_value = request.POST.get('prepayment_value')
        is_prepayment_paid = request.POST.get('is_prepayment_paid') == 'true'
        prepayment_date = request.POST.get('prepayment_date')
        postpayment_value = request.POST.get('postpayment_value')
        is_postpayment_paid = request.POST.get('is_postpayment_paid') == 'true'
        postpayment_date = request.POST.get('postpayment_date')
        address = request.POST.get('address')
        contact_number = request.POST.get('contact_number')
        full_name = request.POST.get('full_name')
        comments = request.POST.get('comments')

        # Create a Client instance
        client = Client(
            first_name=full_name.split()[1],
            last_name=full_name.split()[0] if len(full_name.split()) > 1 else '',
            middle_name=full_name.split()[2] if len(full_name.split()) > 2 else '',
            contact_number=contact_number,
            address=address,
            comments=comments
        )
        client.save()

        # Parse dates and calculate the duration
        create_date_dt = datetime.strptime(create_date, '%Y-%m-%d')
        completion_date_dt = datetime.strptime(completion_date, '%Y-%m-%d')
        duration = (completion_date_dt - create_date_dt).days


        # Create a Contract instance
        contract = Contract(
            num=contract_num,
            client=client,
            create_date=create_date_dt,
            completion_date=completion_date_dt,
            duration=duration,
            total_value=float(total_value),
            total_work_cost=float(total_value),
            payment_type=payment_type,
            prepayment_share=float(prepayment_share),
            prepayment_value=int(prepayment_value),
            is_prepayment_paid=is_prepayment_paid,
            prepayment_date=datetime.strptime(prepayment_date, '%Y-%m-%d') if prepayment_date else None,
            postpayment_value=int(postpayment_value),
            is_postpayment_paid=is_postpayment_paid,
            postpayment_date=datetime.strptime(postpayment_date, '%Y-%m-%d') if postpayment_date else None
        )
        contract.save()

        # Create an Order instance
        manager = Employee.objects.get(id=manager_id)
        new_order = Order(
            number=number,
            manager=manager,
            source=source,
            contract=contract,
            status='registered'
        )
        new_order.save()

        # Associate executors with the order
        for executor_id in executors_ids:
            executor = Employee.objects.get(id=executor_id)
            new_order.executors.add(executor)

        return redirect('orders')

    else:
        context = {
            'managers': managers,
            'executors': executors
        }
        return render(request, 'add_order.html', context)


#СОТРУДНИКИ
def staff_view(request):
    departments = Department.objects.all()
    positions = JobTitle.objects.all()
    employees = Employee.objects.select_related('position', 'department').all()
    total_count = employees.count()

    search_name = request.GET.get('search_name', '')
    if search_name:
        query = Q()
        for term in search_name.split():
            query |= Q(first_name__icontains=term) | Q(last_name__icontains=term) | Q(middle_name__icontains=term)
        employees = employees.filter(query)

    status = request.GET.get('status', '')
    if status:
        employees = employees.filter(status=status)

    department_id = request.GET.get('department', '')
    if department_id:
        employees = employees.filter(department_id=department_id)

    payment_type = request.GET.get('payment_type', '')
    if payment_type:
        employees = employees.filter(type_salary=payment_type)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = [{
            'id': employee.id,
            'full_name': f"{employee.last_name} {employee.first_name} {employee.middle_name}",
            'position': employee.position.name if employee.position else "",
            'department': employee.department.name if employee.department else "",
            'status': employee.get_status_display(),
            'employment_date': employee.employment_date,
            'type_salary': employee.get_type_salary_display(),
            'salary': employee.salary
        } for employee in employees]

        return JsonResponse({'data': data, 'total_count': total_count}, safe=False)

    context = {
        'employees': employees,
        'departments': departments,
        'positions': positions
    }
    return render(request, 'staff.html', context)

@csrf_exempt
def add_employee(request):
    departments = Department.objects.all()
    positions = JobTitle.objects.all()

    if request.method == 'POST':
        # Extract and handle form data
        full_name = request.POST.get('full_name', '').split()
        avatar = request.FILES.get('avatar', None)
        position_id = request.POST.get('position')
        department_id = request.POST.get('department')
        status = request.POST.get('status')
        employment_date = request.POST.get('employment_date')
        termination_date = request.POST.get('termination_date')
        citizenship = request.POST.get('citizenship')
        residence_address = request.POST.get('residence_address')
        passport_series = request.POST.get('passport_series')
        passport_number = request.POST.get('passport_number')
        passport_issued_by = request.POST.get('passport_issued_by')
        passport_issue_date = request.POST.get('passport_issue_date')
        type_salary = request.POST.get('type_salary')
        salary = request.POST.get('salary')
        payment_details = request.POST.get('payment_details')

        # Validate salary input
        try:
            salary = Decimal(salary) if salary.strip() else None
        except (ValueError, TypeError):
            return HttpResponse('Invalid salary input.', status=400)

        # Handle potential IndexError for names
        last_name = full_name[0] if len(full_name) > 0 else ''
        first_name = full_name[1] if len(full_name) > 1 else ''
        middle_name = full_name[2] if len(full_name) > 2 else ''

        # Create new Employee instance
        employee = Employee(
            first_name=first_name, last_name=last_name, middle_name=middle_name,
            avatar=avatar, position_id=position_id, department_id=department_id, status=status,
            employment_date=employment_date, termination_date=termination_date if termination_date else None,
            citizenship=citizenship, residence_address=residence_address,
            passport_series=passport_series, passport_number=passport_number,
            passport_issued_by=passport_issued_by, passport_issue_date=passport_issue_date,
            type_salary=type_salary, salary=salary, payment_details=payment_details
        )
        employee.save()

        return redirect('staff')  # Redirect to the staff list page
    else:
        # Pass positions and departments to the form
        context = {
            'departments': departments,
            'positions': positions
        }
        return render(request, 'add_employee.html', context)

@csrf_exempt
def delete_employee(request, employee_id):
    if request.method == 'POST':
        try:
            employee = Employee.objects.get(pk=employee_id)
            employee.delete()
            return JsonResponse({'success': True})
        except Employee.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Сотрудник не найден'})
    return JsonResponse({'success': False, 'error': 'Неверный запрос'})


@csrf_exempt
def refactor_employee(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    departments = Department.objects.all()
    positions = JobTitle.objects.all()

    if request.method == 'POST':
        # Парсинг данных из формы
        full_name = request.POST.get('full_name', '').split()
        avatar = request.FILES.get('avatar', employee.avatar)

        position_id = request.POST.get('position', employee.position)
        department_id = request.POST.get('department', employee.department)
        position = get_object_or_404(JobTitle, pk=position_id)  # Получаем объект должности
        department = get_object_or_404(Department, pk=department_id)  # Получаем объект отдела

        status = request.POST.get('status', employee.status)
        employment_date = request.POST.get('employment_date', employee.employment_date)
        termination_date = request.POST.get('termination_date', employee.termination_date)
        citizenship = request.POST.get('citizenship', employee.citizenship)
        residence_address = request.POST.get('residence_address', employee.residence_address)
        passport_series = request.POST.get('passport_series', employee.passport_series)
        passport_number = request.POST.get('passport_number', employee.passport_number)
        passport_issued_by = request.POST.get('passport_issued_by', employee.passport_issued_by)
        passport_issue_date = request.POST.get('passport_issue_date', employee.passport_issue_date)
        type_salary = request.POST.get('type_salary', employee.type_salary)

        salary = request.POST.get('salary', employee.salary)
        salary = None if salary == '' else salary

        # Преобразование зарплаты в Decimal, если она не None
        try:
            salary = Decimal(salary) if salary is not None else None
        except (ValueError, TypeError):
            return HttpResponse('Invalid salary input.', status=400)

        payment_details = request.POST.get('payment_details', employee.payment_details)

        # Обновление сотрудника
        employee.avatar = avatar
        employee.first_name = full_name[1] if len(full_name) > 1 else ''
        employee.last_name = full_name[0] if len(full_name) > 0 else ''
        employee.middle_name = full_name[2] if len(full_name) > 2 else ''
        employee.position = position
        employee.department = department
        employee.status = status
        employee.employment_date = employment_date
        employee.termination_date = termination_date if termination_date else None
        employee.citizenship = citizenship
        employee.residence_address = residence_address
        employee.passport_series = passport_series
        employee.passport_number = passport_number
        employee.passport_issued_by = passport_issued_by
        employee.passport_issue_date = passport_issue_date
        employee.type_salary = type_salary
        employee.salary = salary
        employee.payment_details = payment_details
        employee.save()

        return redirect('staff')  # Перенаправление на страницу со списком сотрудников
    else:
        context = {
            'employee': employee,
            'departments': departments,
            'positions': positions
        }
        return render(request, 'refactor_employee.html', context)