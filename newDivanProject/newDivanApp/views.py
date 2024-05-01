from django.shortcuts import render


def main_view(request):
    return render(request, 'main.html')

def calendar_view(request):
    return render(request, 'calendar.html')

def orders_view(request):
    return render(request, 'orders.html')

def active_view(request):
    return render(request, 'active.html')

def staff_view(request):
    return render(request, 'staff.html')