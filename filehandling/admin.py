from django.contrib import admin
from .models import Employee, UploadedExcel

# Register your models here.
admin.site.register(Employee)
admin.site.register(UploadedExcel)