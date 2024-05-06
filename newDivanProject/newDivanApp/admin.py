from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['position', 'department', 'status', 'employment_date', 'avatar', 'first_name', 'last_name',]
    list_filter = ['department', 'status']
    search_fields = ['position', 'department', 'residence_address', 'passport_number']
