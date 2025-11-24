from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import timedelta
from .models import Teacher, Group, Student, Attendance
from django.utils import timezone
import datetime


# -------------------------
# Login / Logout Views
# -------------------------

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Role tekshirish
            if hasattr(user, 'teacher') and user.teacher.role == 'teacher':
                return redirect('teacher_dashboard')  # teacher sahifasi
            else:
                return redirect('home')  # admin sahifasi
        else:
            messages.error(request, "Username yoki password xato")
    return render(request, "login.html")



@login_required
def user_logout(request):
    logout(request)
    return redirect("login")


# -------------------------
# Decorator: Teacher Only
# -------------------------

def teacher_only(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        try:
            request.teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper


# -------------------------
# Home Page
# -------------------------

# views.py
from django.shortcuts import render
from .models import Teacher, Student, Group


def home(request):
    teachers_count = Teacher.objects.count()
    students_count = Student.objects.count()
    groups_count = Group.objects.count()

    context = {
        'teachers_count': teachers_count,
        'students_count': students_count,
        'groups_count': groups_count,
    }
    return render(request, 'home.html', context)


# -------------------------
# Teacher Profile
# -------------------------

@login_required
def teacher_profile(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    groups = Group.objects.filter(teacher=teacher)
    students = Student.objects.filter(group__teacher=teacher)
    return render(request, "teacher_profile.html", {
        "teacher": teacher,
        "groups": groups,
        "student_count": students.count()
    })


# -------------------------
# Group Detail (Davomat)
# -------------------------
from django.shortcuts import render, get_object_or_404
from .models import Group, Attendance


def group_detail(request, id):
    group = get_object_or_404(Group, id=id)
    students = group.students.all()

    DAYS = list(range(1, 19))  # 1..18

    # Attendance ma’lumotlarini yuklab olish
    attendance = Attendance.objects.filter(group=group)

    # har bir student uchun kunlik ma’lumotlar
    attendance_rows = []
    for student in students:
        day_values = []
        for day in DAYS:
            record = attendance.filter(student=student, day_number=day).first()
            day_values.append(record.value if record else "")

        attendance_rows.append({
            "student": student,
            "day_values": day_values,
        })

    # POST – saqlash
    from django.shortcuts import redirect

    # POST qismi
    if request.method == "POST":
        for student in students:
            for day in DAYS:
                key = f"att_{student.id}_{day}"
                value = request.POST.get(key, "").strip()

                obj, created = Attendance.objects.get_or_create(
                    student=student,
                    group=group,
                    day_number=day
                )
                obj.value = value
                obj.save()

        return redirect("group_detail", id=group.id)  # shu sahifaga qaytaradi

    return render(request, "group_detail.html", {
        "group": group,
        "attendance_rows": attendance_rows,
        "days": DAYS,
    })


# -------------------------
# Attendance Toggle (BOR / YO'Q)
# -------------------------

@login_required
def toggle_attendance(request, att_id):
    att = get_object_or_404(Attendance, id=att_id)

    if att.status == "":
        att.status = "bor"
    elif att.status == "bor":
        att.status = "yoq"
    else:
        att.status = ""
    att.save()
    return redirect(request.META.get('HTTP_REFERER'))


# -------------------------
# Add/Edit Group
# -------------------------

@login_required
def group_form(request, id=None):
    if id:
        group = get_object_or_404(Group, id=id)
    else:
        group = None

    teachers = Teacher.objects.all()

    if request.method == "POST":
        title = request.POST.get("title")
        start_date = request.POST.get("start_date")
        teacher_id = request.POST.get("teacher")
        teacher = Teacher.objects.get(id=teacher_id)

        if group:
            group.title = title
            group.start_date = start_date
            group.teacher = teacher
            group.save()
        else:
            Group.objects.create(title=title, start_date=start_date, teacher=teacher)
        return redirect("home")

    return render(request, "group_form.html", {"group": group, "teachers": teachers})


# -------------------------
# Add/Edit Student
# -------------------------

@login_required
def student_form(request, id=None):
    if id:
        student = get_object_or_404(Student, id=id)
    else:
        student = None

    groups = Group.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        group_id = request.POST.get("group")
        group = Group.objects.get(id=group_id)

        if student:
            student.name = name
            student.group = group
            student.save()
        else:
            Student.objects.create(name=name, group=group)
        return redirect("student_list")

    return render(request, "student_form.html", {"student": student, "groups": groups})


@login_required
def add_teacher(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        password = request.POST.get("password")
        phone = request.POST.get("phone")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username allaqachon mavjud")
        else:
            user = User.objects.create_user(username=username, password=password,
                                            first_name=first_name, last_name=last_name)
            Teacher.objects.create(user=user, phone=phone)
            messages.success(request, "Teacher muvaffaqiyatli qo‘shildi")
            return redirect('teacher_list')

    return render(request, "add_teacher.html")


@login_required
def teacher_list(request):
    teachers = Teacher.objects.all()
    return render(request, "teacher_list.html", {"teachers": teachers})


@login_required
def group_list(request):
    groups = Group.objects.all()
    return render(request, "group_list.html", {"groups": groups})


@login_required
def student_list(request):
    students = Student.objects.all()
    return render(request, "student_list.html", {"students": students})


@login_required
def teacher_dashboard(request):
    try:
        teacher = request.user.teacher  # Teacher obyekti olish
    except Teacher.DoesNotExist:
        # Agar Teacher bo'lmasa, boshqa sahifaga yo'naltirish
        return redirect('home')  # yoki login sahifasi

    groups = Group.objects.filter(teacher=teacher)
    students_count = sum([g.students.count() for g in groups])

    context = {
        'teacher': teacher,
        'groups': groups,
        'students_count': students_count,
    }
    return render(request, 'teacher_dashboard.html', context)





from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Teacher


def delete_teacher(request, id):
    teacher = get_object_or_404(Teacher, id=id)

    if request.method == 'POST':
        teacher.user.delete()  # teacher bilan bog‘liq User ham o‘chadi
        messages.success(request, "Teacher successfully deleted!")
        return redirect('teacher_list')

    # GET so‘rov bo‘lsa tasdiqlash sahifasini ko‘rsatish
    return render(request, 'confirm_delete.html', {'teacher': teacher})


from django.shortcuts import render, get_object_or_404, redirect
from .models import Teacher
from django.contrib import messages

def edit_teacher(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            teacher.name = name
            teacher.save()
            messages.success(request, "O‘zgartirish saqlandi!")
            return redirect("teacher_list")  # teacher listga qaytadi
        else:
            messages.error(request, "Iltimos, ismingizni kiriting.")

    return render(request, "edit_teacher.html", {"teacher": teacher})


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Group


def delete_group(request, id):
    group = get_object_or_404(Group, id=id)

    if request.method == 'POST':
        group.delete()
        messages.success(request, "Group successfully deleted!")
        return redirect('teacher_dashboard')  # yoki admin uchun 'group_list'

    # GET so‘rov bo‘lsa tasdiqlash sahifasini ko‘rsatish
    return render(request, 'confirm_delete.html', {'group': group})


from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Student


def delete_student(request, id):
    student = get_object_or_404(Student, id=id)

    if request.method == 'POST':
        student.delete()
        messages.success(request, "Student successfully deleted!")
        return redirect('student_list')

    # GET so‘rov bo‘lsa tasdiqlash sahifasini ko‘rsatish
    return render(request, 'confirm_delete.html', {'student': student})
