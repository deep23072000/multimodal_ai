from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('history/<int:pk>/', views.history_detail, name='history_detail'),
    path('clear-history/', views.clear_history, name='clear_history'),  # ✅ This is the missing one
    path('delete-history/<int:pk>/', views.delete_history, name='delete_history'),  # ✅ For individual deletes
]
