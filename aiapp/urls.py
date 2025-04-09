from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('history/<int:pk>/', views.history_detail, name='history_detail'),
]
