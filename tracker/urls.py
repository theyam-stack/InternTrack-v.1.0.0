from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('applications/', views.internship_list, name='internship_list'),
    path('applications/<int:pk>/', views.internship_detail, name='internship_detail'),
    path('create/', views.internship_create, name='internship_create'),
    path('<int:pk>/update/', views.internship_update, name='internship_update'),
    path('<int:pk>/delete/', views.internship_delete, name='internship_delete'),
    path('<int:pk>/interview/add/', views.interview_create, name='interview_create'),

    path('companies/', views.company_list, name='company_list'),
    path('search/', views.search, name='search'),
    path('interviews/', views.interview_list, name='interview_list'),
    path('settings/', views.settings_view, name='settings'),

    # Auth
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),

    # Backend Dev 2 routes
    path('export/', views.export_page, name='export_page'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
]