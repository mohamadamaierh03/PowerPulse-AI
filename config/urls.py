from django.contrib import admin
from django.urls import path, include
from core.views import whatsapp_webhook 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('whatsapp/message/', whatsapp_webhook, name='whatsapp_webhook'), 
    
]