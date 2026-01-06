from django.db import models

# Create your models here.
class Employee(models.Model):
    name = models.CharField(max_length=500, null=False)
    emp_id = models.CharField(max_length=7, null=False, primary_key=True)
    issue_date = models.DateField(null=False)
    joining_date = models.DateField(null=False)
    blood_group = models.CharField(null=False)
    expiry_date = models.DateField(null=False)
    NID_number = models.CharField(null=False)
    emergency = models.CharField(null=True, max_length=11)
    image = models.ImageField(null=True)
    designation = models.CharField(max_length=100, null=True)
    excel = models.ForeignKey("UploadedExcel", on_delete=models.CASCADE, blank=True, null=True)
    card_generated = models.BooleanField(default=False)

    def __str__(self):
        return self.name 

class UploadedExcel(models.Model):
    file = models.FileField(upload_to='excels/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return self.file.name.split('/')[-1]