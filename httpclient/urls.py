from django.urls import path
from .views import CallAPIView

urlpatterns = [
    path('call-api/', CallAPIView.as_view(), name='call_api'),
]