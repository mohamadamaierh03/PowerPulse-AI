import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import EnergyConsumer, ServiceTicket
from core.flows.energy_flow import EnergyManagementFlow
from asgiref.sync import sync_to_async
import asyncio

async def run_test_scenario():
    print("🚀 Starting PowerPulse AI Test Scenario...")

    user, _ = await sync_to_async(User.objects.get_or_create)(username="mohammad_tester")
    
    consumer, _ = await sync_to_async(EnergyConsumer.objects.get_or_create)(
        user=user,
        defaults={
            'meter_number': 'JO-998877',
            'address': 'Amman, Jordan',
            'average_consumption': 450.5
        }
    )

    ticket = await sync_to_async(ServiceTicket.objects.create)(
        consumer=consumer,
        issue_description="There is a strange burning smell near the main circuit breaker panel.",
        urgency='high'
    )

    flow = EnergyManagementFlow()
    flow.state['user_query'] = ticket.issue_description
    flow.state['consumer_id'] = consumer.id
    flow.state['ticket_id'] = ticket.id
    
    print(f"--- Processing Ticket ID: {ticket.id} ---")
    
    result = await flow.kickoff_async()
    
    print("\n" + "="*50)
    print("✅ TEST COMPLETED")
    print("="*50)
    print(f"AI Final Output: {result}")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(run_test_scenario())