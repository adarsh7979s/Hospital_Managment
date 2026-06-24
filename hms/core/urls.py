from django.urls import path
from core import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect_view, name='dashboard'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/add-availability/', views.add_availability, name='add_availability'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/book/', views.book_appointment, name='book_appointment'),
    path('google/login/', views.google_auth_redirect, name='google_auth_redirect'),
    path('google/callback/', views.google_auth_callback, name='google_auth_callback'),
]
