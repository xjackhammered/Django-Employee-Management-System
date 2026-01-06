from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("upload/", views.upload_excel, name="excel-upload"),
    path("employee-list/",views.employee_list, name="employee-list"),
    path("employee/<str:emp_id>/",views.emergency, name="emergency-contact"),
    path("image/<str:emp_id>",views.image_handling, name="image"),
    path('generate-id-card/<str:emp_id>/', views.generate_card, name='generate-id-card'),
    path('update-employee/<str:emp_id>/',views.updateEmployee, name="update-employee"),
    path("delete-employee/<str:emp_id>/",views.deleteEmployee, name="delete-employee"),
    path("create-employee/",views.createEmployee, name="create-employee"),
    path("home/", views.home_view, name="home"),
    path("upload-details/<int:id>/", views.upload_details, name="upload-details"),
    path('designation/<str:emp_id>/', views.handleDesignation, name='designation'),
    path("generate-all-ids/", views.generate_all_cards_pdf, name="generate-all-ids"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)