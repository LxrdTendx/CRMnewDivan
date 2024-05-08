from django.db import models
from django.core.validators import FileExtensionValidator

# ******** СУЩНОСТИ, СВЯЗАННЫЕ С ЗАВЕДЕНИЕМ РАБОТНИКА ********* #
# таблица с описанием отделов на производства
class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название отдела")
    descr = models.TextField(blank=True, null=True, verbose_name="Описание отдела")

    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"

    def __str__(self):
        return self.name

# таблица с описанием занимаемых должностей на производстве
class JobTitle(models.Model):
    name = models.CharField(max_length=100, verbose_name="Должность")
    descr = models.TextField(blank=True, null=True, verbose_name="Описание")
    min_salary = models.IntegerField(blank=True, null=True, verbose_name="Минимальное значение зарплаты для должности")
    max_salary = models.IntegerField(blank=True, null=True, verbose_name="Максимальное значение зарплаты для должности")
    access_lvl = models.IntegerField(null=True, verbose_name="Уровень доступа")

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"

    def __str__(self):
        return self.name

class Employee(models.Model):
    STATUS_CHOICES = (
        ('working', 'работает'),
        ('not_working', 'уволен'),
        ('probation', 'испытательный срок'),
    )

    # DEPARTMENT_CHOICES = (
    #     ('office', 'Офис'),
    #     ('workshop', 'Цех'),
    # )
    SALARY_CHOICES = (
        ('fixed', "фиксированный"),
        ('not_fixed', "сдельный")
    )


    first_name = models.CharField(max_length=100, verbose_name="Имя", null=True)
    last_name = models.CharField(max_length=100, verbose_name="Фамилия", null=True)
    middle_name = models.CharField(max_length=100, verbose_name="Отчество", blank=True, null=True)
    position = models.ForeignKey(JobTitle, on_delete=models.CASCADE, verbose_name="Должность", null=True)  # внешний ключ к таблице должностей
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Отдел", null=True) # внешний ключ к таблице отделов
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
    salary = models.IntegerField(verbose_name="Зарплата", null=True)
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


# ******** СУЩНОСТИ, СВЯЗАННЫЕ С ЗАВЕДЕНИЕМ ЗАКАЗА ********* #

# сводная таблица с описанием данных заказа
class Order(models.Model):
    ORDER_STATUS = (
        ('registered', 'Заказ зарегистрирован'),
        ('to_pickup', 'Необходимо забрать'),
        ('is_picked', 'Заказ привезли'),
        ('to_do', 'В очереди'),
        ('in_progress', 'Взято в работу'),
        ('in_review', 'Ждет проверки управляющего'),
        ('closed', 'Выполнено успешно'),
        ('suspended', 'Приостановлено'),
        ('to_deliver', 'Необходима доставка'),
        ('delivered', 'Доставлено клиенту'),
    )

    number = models.CharField(max_length=100, verbose_name="Номер заказа")
    contract = models.ForeignKey('Contract', on_delete=models.CASCADE, verbose_name="Договор")
    manager = models.ForeignKey('Employee', on_delete=models.CASCADE, verbose_name="Менеджер",
                                related_name="managed_orders")
    status = models.CharField(max_length=100, choices=ORDER_STATUS, verbose_name="Статус заказа")
    executor1 = models.ForeignKey('Employee', on_delete=models.CASCADE, verbose_name="Исполнитель 1",
                                  related_name="executor1_orders", blank=True, null=True)
    executor2 = models.ForeignKey('Employee', on_delete=models.CASCADE, verbose_name="Исполнитель 2",
                                  related_name="executor2_orders", blank=True, null=True)
    executor3 = models.ForeignKey('Employee', on_delete=models.CASCADE, verbose_name="Исполнитель 3",
                                  related_name="executor3_orders", blank=True, null=True)
    comments = models.TextField(blank=True, null=True, verbose_name="Комментарии")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return self.number

    # employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    # def save(self, args, **kwargs):
    #     self.manager = f"{self.employee.first_name} {self.employee.second_name} {self.employee.middle_name}"
    #     super().save(args, **kwargs)


# таблица техзадания
class TechnicalSpecification(models.Model):
    WORK_TYPES = (
        ('create', 'Изготовление'),
        ('reupholster', 'Перетяжка'),
        ('restoration', 'Реставрация'),
        ('new_build', 'Новодел')
    )

    FURNITURE_TYPES = (
        ('soft', 'Мягкая мебель'),
        ('cabinet', 'Корпусная мебель'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    items_qty = models.PositiveIntegerField(verbose_name="Кол-во изделий")
    short_descr = models.CharField(max_length=100, verbose_name="Краткое описание ТЗ")
    full_descr = models.TextField(blank=True, default='', verbose_name="Полное описание ТЗ")
    work_type1 = models.CharField(max_length=50, choices=WORK_TYPES, verbose_name="Тип работ 1")
    work_type2 = models.CharField(max_length=50, choices=WORK_TYPES, verbose_name="Тип работ 2", null=True, blank=True)
    furniture_type1 = models.CharField(max_length=50, choices=FURNITURE_TYPES, verbose_name="Тип мебели 1")
    furniture_type2 = models.CharField(max_length=50, choices=FURNITURE_TYPES, verbose_name="Тип мебели 2", null=True,
                                       blank=True)
    comments = models.TextField(blank=True, null=True, verbose_name="Комментарии к ТЗ")
    photo1 = models.ImageField(upload_to='technical_specifications/', verbose_name="Фото 1", null=True, blank=True,
                               validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    photo2 = models.ImageField(upload_to='technical_specifications/', verbose_name="Фото 2", null=True, blank=True,
                               validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    photo3 = models.ImageField(upload_to='technical_specifications/', verbose_name="Фото 3", null=True, blank=True,
                               validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    photo4 = models.ImageField(upload_to='technical_specifications/', verbose_name="Фото 4", null=True, blank=True,
                               validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])

    class Meta:
        verbose_name = "Техзадание"
        verbose_name_plural = "Техзадания"

    def __str__(self):
        return f"Техзадание для {self.order.number}"


# таблица активностей
class Activity(models.Model):
    ACTIVITY_STATUS = (
        ('backlog', 'Активность зарегистрирована'),
        ('in_review', 'Ждет проверки управляющего'),
        ('to_do', 'К выполнению работником'),
        ('in_progress', 'Взято в работу'),
        ('closed_positive', 'Выполнено успешно'),
        ('closed_negative', 'Выполнено неуспешно'),
        ('needs_rework', 'Необходима доработка'),
        ('suspended', 'Приостановлено'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, verbose_name="Ответственный",
                                 related_name="activities")
    activity_descr = models.TextField(blank=True, verbose_name="Описание работы")
    status = models.CharField(max_length=100, choices=ACTIVITY_STATUS, default='backlog',
                              verbose_name="Статус активности")
    date_start = models.DateField(verbose_name="Дата начала")
    date_review = models.DateField(verbose_name="Дата проверки управляющим", null=True, blank=True)
    date_end = models.DateField(verbose_name="Дата окончания", blank=True, null=True)
    total_work_cost = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Общая стоимость работы")
    is_paid = models.BooleanField(default=False, verbose_name="Оплата произведена")
    payment_date = models.DateField(verbose_name="Дата оплаты", blank=True, null=True)
    photo1 = models.ImageField(upload_to='activity/', verbose_name="Фото 1", null=True, blank=True,
                               validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    photo2 = models.ImageField(upload_to='activity/', verbose_name="Фото 2", null=True, blank=True,
                               validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    photo3 = models.ImageField(upload_to='activity/', verbose_name="Фото 3", null=True, blank=True,
                               validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    photo4 = models.ImageField(upload_to='activity/', verbose_name="Фото 4", null=True, blank=True,
                               validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])

    class Meta:
        verbose_name = "Активность"
        verbose_name_plural = "Активности"

    def __str__(self):
        return f"Активность {self.id}"


class Material(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    material_name = models.CharField(max_length=100, verbose_name="Наименование материала")
    material_in_stock = models.BooleanField(default=False, verbose_name="Материал в наличии на складе")
    material_cost = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Стоимость материала', null=True,
                                        blank=True)
    is_ordered = models.BooleanField(default=False, verbose_name="Заказан")
    material_payment_status = models.CharField(max_length=100, verbose_name="Статус оплаты материала", choices=(
    ('paid', 'Оплачено'), ('unpaid', 'Не оплачено'), ('partial', 'Частично оплачено')), blank=True)
    material_payment_date = models.DateField(verbose_name="Дата оплаты материала", blank=True, null=True)
    needs_fitting = models.BooleanField(default=False, verbose_name="Требуется фурнитура")
    fitting_name = models.CharField(max_length=100, verbose_name="Наименование фурнитуры", blank=True, null=True)
    fitting_in_stock = models.BooleanField(default=False, verbose_name="Фурнитура в наличии на складе", blank=True,
                                           null=True)
    comments = models.TextField(blank=True, verbose_name="Комментарии", null=True)

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"

    def __str__(self):
        return f"{self.order.number} - {self.material_name}"


class PickupDelivery(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    is_picked = models.BooleanField(default=False, verbose_name="Забран")
    pickup_type = models.CharField(max_length=50, verbose_name="Тип забора",
                                   choices=(('self_delivery', 'Самовывоз'), ('pickup', 'Забор')))
    estimated_pickup_date = models.DateField(verbose_name="Планируемая дата забора", null=True, blank=True)
    actual_pickup_date = models.DateField(null=True, blank=True, verbose_name="Фактическая дата забора")
    is_delivered = models.BooleanField(default=False, verbose_name="Доставлен")
    delivery_type = models.CharField(max_length=50, verbose_name="Тип доставки",
                                     choices=(('self_delivery', 'Самовывоз'), ('delivery', 'Доставка')))
    estimated_delivery_date = models.DateField(verbose_name="Планируемая дата доставки", null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True, verbose_name="Фактическая дата доставки")
    delivery_guy = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Доставщик", null=True,
                                     blank=True)
    comments = models.TextField(blank=True, null=True, verbose_name="Комментарии")

    class Meta:
        verbose_name = "Забор/Доставка"
        verbose_name_plural = "Заборы/Доставки"




# ******** СУЩНОСТИ, СВЯЗАННЫЕ С ЗАВЕДЕНИЕМ ДОГОВОРА ********* #

#  таблица с информацией о клиентах (физ лица)
class Client(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=100, verbose_name="Отчество", blank=True, null=True)
    contact_number = models.CharField(max_length=20, verbose_name="Контактный телефон")
    address = models.TextField(verbose_name="Адрес", blank=True, null=True)
    comments = models.TextField(blank=True, null=True, verbose_name="Комментарии к клиенту")

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


#  таблица с информацией о клиентах-компаниях (юр лица)
class Firm(models.Model):
    contact = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Контактное лицо")
    short_name = models.CharField(max_length=100, verbose_name="Краткое наименование компании")
    full_name = models.CharField(max_length=255, verbose_name="Полное наименование компании")
    legal_address = models.TextField(verbose_name="Юридический адрес")
    actual_address = models.TextField(verbose_name="Фактический адрес")
    INN = models.CharField(max_length=12, verbose_name="ИНН", blank=True, null=True)
    KPP = models.CharField(max_length=9, verbose_name="КПП", blank=True, null=True)
    OGRN = models.CharField(max_length=15, verbose_name="ОГРН", blank=True, null=True)
    contact_number = models.CharField(max_length=20, verbose_name="Контактный телефон")
    corporate_number = models.CharField(max_length=20, verbose_name="Корпоративный номер", null=True)
    comments = models.TextField(blank=True, null=True, verbose_name="Комментарии")

    class Meta:
        verbose_name = "Клиентская фирма"
        verbose_name_plural = "Клиентские фирмы"

    def __str__(self):
        return self.short_name


# таблица с информацией о заключенном договоре с клиентом
class Contract(models.Model):
    num = models.CharField(max_length=100, verbose_name="Номер договора")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент")
    firm = models.ForeignKey(Firm, on_delete=models.CASCADE, verbose_name="Фирма", null=True, blank=True)
    create_date = models.DateField(verbose_name="Дата создания")
    completion_date = models.DateField(verbose_name="Ориентировочная дата выполнения")
    duration = models.IntegerField(verbose_name="Сроки выполнения по договору")
    total_value = models.DecimalField(max_digits=12, decimal_places=2,
                                      verbose_name="Общая стоимость заказа по договору")
    total_work_cost = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Общая стоимость работ")
    prepayment_share = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Процент предоплаты")
    prepayment_value = models.IntegerField(verbose_name="Сумма предоплаты")
    prepayment_date = models.DateField(verbose_name="Дата предоплаты", blank=True, null=True)
    is_prepayment_paid = models.BooleanField(default=False, verbose_name="Предоплата произведена")
    payment_date = models.DateField(verbose_name="Дата оплаты", blank=True, null=True)
    is_balance_paid = models.BooleanField(default=False, verbose_name="Оплата произведена")
    comments = models.TextField(blank=True, null=True, verbose_name="Комментарии к договору")

    class Meta:
        verbose_name = "Договор"
        verbose_name_plural = "Договоры"

    def __str__(self):
        return f"{self.num} от {self.create_date}"