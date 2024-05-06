from django.db import models
from django.core.validators import FileExtensionValidator

class Employee(models.Model):
    STATUS_CHOICES = (
        ('working', 'Работает'),
        ('not_working', 'Не работает'),
        ('probation', 'Испытательный срок'),
    )

    DEPARTMENT_CHOICES = (
        ('office', 'Офис'),
        ('workshop', 'Цех'),
    )
    SALARY_CHOICES = (
        ('fixed', "Фиксированная"),
        ('not_fixed', "Сдельная")
    )


    first_name = models.CharField(max_length=100, verbose_name="Имя", null=True)
    last_name = models.CharField(max_length=100, verbose_name="Фамилия", null=True)
    middle_name = models.CharField(max_length=100, verbose_name="Отчество", blank=True, null=True)
    position = models.CharField(max_length=100, verbose_name="Должность")
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, verbose_name="Подразделение")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, verbose_name="Статус")
    employment_date = models.DateField(verbose_name="Дата приема на работу")
    termination_date = models.DateField(blank=True, null=True, verbose_name="Дата увольнения")
    citizenship = models.CharField(max_length=50, verbose_name="Гражданство")
    residence_address = models.CharField(max_length=255, verbose_name="Адрес проживания")
    passport_series = models.CharField(max_length=10, verbose_name="Серия")
    passport_number = models.CharField(max_length=50, verbose_name="Номер")
    passport_issued_by = models.CharField(max_length=255, verbose_name="Кем выдан")
    passport_issue_date = models.DateField(verbose_name="Дата выдачи")
    type_salary = models.TextField(verbose_name="Тип оплаты", choices=SALARY_CHOICES, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Зарплата", null=True)
    payment_details = models.TextField(verbose_name="Реквизиты оплаты")
    avatar = models.ImageField(
        upload_to='avatars/',
        verbose_name="Аватар",
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name} - {self.position}"

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
