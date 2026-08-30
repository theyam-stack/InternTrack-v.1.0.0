from django.urls import path
from . import views

urlpatterns = [
    path('', views.internship_list, name='internship_list'),
    path('create/', views.internship_create, name='internship_create'),
    path('<int:pk>/update/', views.internship_update, name='internship_update'),
    path('<int:pk>/delete/', views.internship_delete, name='internship_delete'),
]