from django.contrib import admin
from .models import EnergyConsumer, ServiceTicket, GeneratedEnergyContent

@admin.register(EnergyConsumer)
class EnergyConsumerAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'user', 'meter_number', 'average_consumption')
    search_fields = ('phone_number', 'meter_number')

@admin.register(ServiceTicket)
class ServiceTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'consumer', 'category', 'status', 'urgency', 'created_at')
    list_filter = ('status', 'category', 'urgency')
    search_fields = ('ticket_id', 'consumer__phone_number')

@admin.register(GeneratedEnergyContent)
class GeneratedEnergyContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'created_at', 'whatsapp_sid')
    readonly_fields = ('created_at', 'prompt_used', 'generated_text', 'image_url')