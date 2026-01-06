from django import forms
from django.forms import ModelForm
from .models import Employee, UploadedExcel

class ExcelForm(forms.ModelForm):
    class Meta:
        model = UploadedExcel
        fields = ['file']

class EmergencyForm(ModelForm):
    class Meta:
        model = Employee
        fields = ['emergency']

class ImageForm(ModelForm):
    class Meta:
        model = Employee
        fields = ['image']

class EmployeeForm(ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        exclude = ['excel', 'card_generated']

class DesignationForm(ModelForm):
    class Meta:
        model = Employee
        fields = ['designation']