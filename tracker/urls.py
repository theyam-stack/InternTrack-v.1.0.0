from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.internship_list, name='internship_list'),
    path('create/', views.internship_create, name='internship_create'),
    path('<int:pk>/update/', views.internship_update, name='internship_update'),
    path('<int:pk>/delete/', views.internship_delete, name='internship_delete'),
    
    # ระบบ Auth
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
]