from django.db import models
from django.contrib.auth.models import User

class EnergyConsumer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True) 
    meter_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    average_consumption = models.FloatField(default=0.0, help_text="Average monthly consumption in kWh")

    def __str__(self):
        return f"{self.phone_number} - {self.user.username if self.user else 'WhatsApp Guest'}"

class ServiceTicket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    CATEGORY_CHOICES = [
        ('emergency', 'Emergency'),
        ('technical_fault', 'Technical Fault'),
        ('energy_advice', 'Energy Advice'),
    ]
    URGENCY_CHOICES = [
        ('low', 'Low (Consultation)'),
        ('high', 'High (Danger/Power Outage)'),
    ]

    consumer = models.ForeignKey(EnergyConsumer, on_delete=models.CASCADE, related_name='tickets')
    ticket_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    issue_description = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='energy_advice')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='low')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket {self.ticket_id or self.id} - {self.consumer.phone_number}"

class GeneratedEnergyContent(models.Model):
    ticket = models.ForeignKey(ServiceTicket, on_delete=models.SET_NULL, null=True, related_name='ai_content')
    prompt_used = models.TextField()
    generated_text = models.TextField(null=True, blank=True)
    
    image_url = models.URLField(max_length=1000, null=True, blank=True)
    
    generated_image = models.ImageField(upload_to='generated_images/', null=True, blank=True)
    
    whatsapp_sid = models.CharField(max_length=100, null=True, blank=True) # تتبع حالة الإرسال في تويليو
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Response for Ticket {self.ticket.ticket_id if self.ticket else 'N/A'}"