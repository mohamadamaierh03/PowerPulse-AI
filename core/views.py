from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse
from asgiref.sync import sync_to_async
import asyncio
import threading

from django.contrib.auth.models import User
from core.models import EnergyConsumer, ServiceTicket
from core.flows.energy_flow import PowerPulseFlow 

def start_flow_thread(message_body, from_number):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_flow_logic(message_body, from_number))
    loop.close()

async def run_flow_logic(message_body, from_number):
    try:
        user, _ = await sync_to_async(User.objects.get_or_create)(username="whatsapp_user")
        consumer, _ = await sync_to_async(EnergyConsumer.objects.get_or_create)(
            user=user,
            defaults={'meter_number': f'WA-{from_number[-8:]}', 'average_consumption': 350.0}
        )
        ticket = await sync_to_async(ServiceTicket.objects.create)(
            consumer=consumer,
            issue_description=message_body,
            urgency='high' if any(word in message_body.lower() for word in ['spark', 'fire', 'smoke']) else 'normal'
        )

        print(f"⚙️ PowerPulse AI Flow started for Ticket #{ticket.id}")
        flow = PowerPulseFlow()
        
        
        await flow.kickoff_async(
            user_query=message_body, 
            whatsapp_to=from_number
        )
        
        print(f"🏁 Flow completed for Ticket #{ticket.id}")
    except Exception as e:
        print(f"❌ Error in Flow Logic: {e}")

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'POST':
        incoming_msg = request.POST.get('Body', '').strip()
        from_number = request.POST.get('From', '').strip()

        print(f"✅ Received from {from_number}: {incoming_msg}")

        thread = threading.Thread(target=start_flow_thread, args=(incoming_msg, from_number))
        thread.start()

        resp = MessagingResponse()
        return HttpResponse(str(resp), content_type='application/xml')
    
    return HttpResponse("Method Not Allowed", status=405)