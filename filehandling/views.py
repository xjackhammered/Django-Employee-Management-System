from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .forms import ExcelForm, EmergencyForm, ImageForm, EmployeeForm, DesignationForm
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from .models import Employee, UploadedExcel
import pandas as pd
import os
from django.core.paginator import Paginator
from django.http import FileResponse
from io import BytesIO


def home_view(request):
    excel = UploadedExcel.objects.all()
    paginator = Paginator(excel, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "filehandling/home.html", {"page_obj":page_obj})

def upload_details(request, id):
    uploads = UploadedExcel.objects.get(id=id)

    if request.GET.get('q') != None:
        q = request.GET.get('q')
        upload_employees = uploads.employee_set.filter(emp_id__iexact=q)
    else:
        upload_employees = uploads.employee_set.all()
    
    paginator = Paginator(upload_employees, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "filehandling/upload_details.html", {"page_obj":page_obj, "uploads":uploads})

def upload_excel(request):
    if request.method == 'POST':
        form = ExcelForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            uploaded_excel = UploadedExcel.objects.create(file=excel_file)
            
            df = pd.read_excel(uploaded_excel.file.path, header=1)
            df.columns = df.columns.str.strip().str.replace('\n', '', regex=False).str.replace('\xa0', ' ', regex=False)

            employees_to_create = []
            for _, row in df.iterrows():
                try:
                    emp = Employee(
                        name=row.get('Name'),
                        emp_id=row.get('ID'),
                        issue_date=row.get('Date of Issue'),
                        joining_date=row.get('Date of Joining'),
                        blood_group=row.get('Blood group'),
                        expiry_date=row.get('Expiary date'),
                        NID_number=row.get('NID Number'),
                        emergency=row.get('Emergency Contact'),
                        designation = row.get('Designation'),
                        excel=uploaded_excel
                    )
                    employees_to_create.append(emp)
                except Exception as e:
                    print("Row skipped:", row.to_dict())
                    print("Error:", e)

            Employee.objects.bulk_create(employees_to_create)

            return redirect('employee-list')
    else:
        form = ExcelForm()
    return render(request, 'filehandling/upload.html', {'form': form})


def employee_list(request):
    
    if request.GET.get('q') != None:
        q = request.GET.get('q')
        employees = Employee.objects.filter(emp_id__iexact=q)
    else:
        employees = Employee.objects.all()
    
    paginator = Paginator(employees, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "filehandling/employee_list.html", {"page_obj":page_obj})


def emergency(request, emp_id):
    employee = Employee.objects.get(emp_id=emp_id)

    if request.method == "POST":
        form = EmergencyForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee-list')
    else:
        form = EmergencyForm(instance=employee)

    return render(request, 'filehandling/emergency_contact.html', {"form": form})

def image_handling(request, emp_id):
    employee = Employee.objects.get(emp_id=emp_id)

    if request.method == "POST":
        form = ImageForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee-list')
    else:
        form = ImageForm(instance=employee)

    return render(request, "filehandling/image.html", {"form": form})

def generate_card(request, emp_id):
    from .models import Employee
    employee = get_object_or_404(Employee, emp_id=emp_id)

    template_path = os.path.join(settings.BASE_DIR, "static/images/id.jpg")
    card = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(card)

    font_path = os.path.join(settings.BASE_DIR, "static/fonts/")
    def load_font(name, size):
        try:
            return ImageFont.truetype(os.path.join(font_path, name), size)
        except:
            return ImageFont.load_default()

    bold = load_font("arialbd.ttf", 100)
    regular = load_font("arialbd.ttf", 33)
    small_bold = load_font("arialbd.ttf", 35)
    blood_group = load_font("arialbd.ttf",35)
    design = load_font("arialbd.ttf",32)
    
    if len(employee.name) <= 8:
        draw.text((305, 750), employee.name, font=bold, fill=(0, 0, 120))
    else:
        draw.text((232, 750), employee.name, font=bold, fill=(0, 0, 120))
    draw.text((300, 910), f"{employee.emp_id}", font=small_bold, fill="black")
    draw.text((405, 1040), f"{employee.joining_date.strftime('%d/%b/%Y')}", font=regular, fill="black")
    draw.text((1295, 466), f"{employee.blood_group}", font=blood_group, fill="black")
    draw.text((1150, 992), f"{employee.expiry_date.strftime('%d/%b/%Y')}", font=regular, fill="black")
    draw.text((1090, 1064), f"{employee.NID_number}", font=regular, fill="black")
    draw.text((1260, 1165), f"{employee.emergency}", font=regular, fill="white")
    draw.text((250, 840), f"{employee.designation}", font=design, fill="gray")


    if employee.image:
        try:
            photo = Image.open(employee.image.path).resize((299, 336))  #frame
            card.paste(photo, (219, 280))  #photo box
        except Exception as e:
            print(f"Error loading photo: {e}")

    
    response = HttpResponse(content_type="image/png")
    card.save(response, "PNG")
    
    
    employee.card_generated = True
    employee.save()
    
    return response


def createEmployee(request):
    form = EmployeeForm

    if request.method == "POST":
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.save()
            return redirect("employee-list")
    
    return render(request, "filehandling/employee_update.html", {"form":form})


def updateEmployee(request, emp_id):
    employee = Employee.objects.get(emp_id=emp_id)

    if request.method == "POST":
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            return redirect("employee-list")
    else:
        form = EmployeeForm(instance=employee)
        
    return render(request, 'filehandling/employee_update.html', {"form":form})


def deleteEmployee(request, emp_id):
    employee = Employee.objects.get(emp_id=emp_id)
    if request.method == "POST":
        employee.delete()
        return redirect("employee-list")
    return render(request, "filehandling/delete.html",{"employee":employee})

def handleDesignation(request, emp_id):
    employee = Employee.objects.get(emp_id=emp_id)
    form = DesignationForm()

    if request.method == "POST":
        form = DesignationForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect("employee-list")
    return render(request, "filehandling/designation.html", {"form":form})

def generate_all_cards_pdf(request):
    
    employees = Employee.objects.filter(card_generated = True)

    images = []
    for employee in employees:
        
        template_path = os.path.join(settings.BASE_DIR, "static/images/id.jpg")
        card = Image.open(template_path).convert("RGBA")
        draw = ImageDraw.Draw(card)

        font_path = os.path.join(settings.BASE_DIR, "static/fonts/")
        def load_font(name, size):
            try:
                return ImageFont.truetype(os.path.join(font_path, name), size)
            except:
                return ImageFont.load_default()

        bold = load_font("arialbd.ttf", 40)
        regular = load_font("arialbd.ttf", 33)
        small_bold = load_font("arialbd.ttf", 35)
        blood_group = load_font("arialbd.ttf", 35)
        design = load_font("arialbd.ttf", 32)

        if len(employee.name) <= 8:
            draw.text((305, 750), employee.name, font=bold, fill=(0, 0, 120))
        else:
            draw.text((232, 750), employee.name, font=bold, fill=(0, 0, 120))
        draw.text((300, 910), f"{employee.emp_id}", font=small_bold, fill="black")
        draw.text((405, 1040), f"{employee.joining_date.strftime('%d/%b/%Y')}", font=regular, fill="black")
        draw.text((1295, 466), f"{employee.blood_group}", font=blood_group, fill="black")
        draw.text((1150, 992), f"{employee.expiry_date.strftime('%d/%b/%Y')}", font=regular, fill="black")
        draw.text((1090, 1064), f"{employee.NID_number}", font=regular, fill="black")
        draw.text((1260, 1165), f"{employee.emergency}", font=regular, fill="white")
        draw.text((250, 840), f"{employee.designation}", font=design, fill="gray")

        if employee.image:
            try:
                photo = Image.open(employee.image.path).resize((309, 390))
                card.paste(photo, (223, 317))
            except Exception as e:
                print(f"Error loading photo for {employee.name}: {e}")

        
        images.append(card.convert("RGB"))

    if not images:
        return HttpResponse("No ID cards to generate.", status=404)

    buffer = BytesIO()
    images[0].save(buffer, format="PDF", save_all=True, append_images=images[1:])
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename="all_id_cards.pdf")
