# In myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('process', views.process_receipts, name='process_receipts'),
    path('<int:receipt_id>/points', views.points_for_receipt, name='get_receipt'),
]
