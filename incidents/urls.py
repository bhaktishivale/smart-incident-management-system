from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('incidents/', views.incident_list, name='incident_list'),
    path('incidents/add/', views.incident_create, name='incident_create'),
    path('incidents/<int:pk>/edit/', views.incident_update, name='incident_update'),
    path('incidents/<int:pk>/delete/', views.incident_delete, name='incident_delete'),
]
