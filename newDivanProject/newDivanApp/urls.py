from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.main_view, name='main'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('orders/', views.orders_view, name='orders'),
    path('active/', views.active_view, name='active'),
    path('staff/', views.staff_view, name='staff'),

]

# Добавление маршрутов для обслуживания медиа-файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
