from django.urls import path
from . import views
from .views import group_detail

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path("group/<int:id>/", group_detail, name="group_detail"),
    path('att-toggle/<int:att_id>/', views.toggle_attendance, name='att_toggle'),

    path('group/add/', views.group_form, name='add_group'),
    path('group/edit/<int:id>/', views.group_form, name='edit_group'),
    path('student/add/', views.student_form, name='add_student'),
    path('student/edit/<int:id>/', views.student_form, name='edit_student'),

    path('teacher/add/', views.add_teacher, name='add_teacher'),
    path('teacher/list/', views.teacher_list, name='teacher_list'),
    path('group/list/', views.group_list, name='group_list'),
    path('student/list/', views.student_list, name='student_list'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('group/<int:id>/delete/', views.delete_group, name='delete_group'),

    path('teachers/<int:id>/', views.teacher_profile, name='teacher_profile'),
    path('teachers/<int:pk>/edit/', views.edit_teacher, name='edit_teacher'),
    path('teachers/<int:id>/delete/', views.delete_teacher, name='delete_teacher'),
    path('students/<int:id>/delete/', views.delete_student, name='delete_student'),

]
