import asyncio
import json
import logging
import re
from django.conf import settings
from crewai.flow import Flow, listen, start, router, or_
import uuid
from core.models import EnergyConsumer, ServiceTicket, GeneratedEnergyContent

from core.crews import PowerPulseCrew 
from core.tools.whatsapp_sender import send_energy_update_to_whatsapp
from .schema import ContentGenerationState
from core.main_llm import basic_llm 

logger = logging.getLogger(__name__)

class PowerPulseFlow(Flow[ContentGenerationState]):

    @start()
    def analyze_request(self):
        print(f"🔍 Analyzing Request: {self.state.user_query}")
        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a Power Systems Dispatcher. Categorize the input into: "
                        "'emergency', 'technical_fault', or 'energy_advice'. "
                        "Return ONLY a JSON object: {'category': '...'}"
                    ),
                },
                {
                    "role": "user",
                    "content": self.state.user_query
                },
            ]
            response = basic_llm.call(messages=messages)
            
            if isinstance(response, dict):
                self.state.planner_output = response
            else:
                self.state.planner_output = json.loads(response)
                
            return self.state.planner_output

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            self.state.planner_output = {"category": "energy_advice"}
            return self.state.planner_output

    @router(analyze_request)
    def energy_router(self):
        category = self.state.planner_output.get("category", "energy_advice")
        print(f"🎯 Route determined: {category}")
        return category

    @listen(or_("energy_advice", "technical_fault"))
    async def run_power_pulse_crew(self):
        print(f"🚀 Launching PowerPulseCrew for {self.state.planner_output['category']}...")
        
        result = await PowerPulseCrew().crew().kickoff_async(
            inputs={"user_query": self.state.user_query}
        )
        
        self.state.text_generation_output = {"text": result.raw}
        
        
        if "http" in result.raw:
            image_pattern = r'(https?://\S+\.(?:png|jpe?g|gif|webp)(?:\?\S*)?)'
            links = re.findall(image_pattern, result.raw, re.IGNORECASE)
            
            if links:
                clean_link = links[0].strip('()[]{},. ')
                self.state.image_generation_output = {"url": clean_link}
                print(f"🖼️ Image URL extracted successfully: {clean_link}")
            else:
                all_links = re.findall(r'(https?://\S+)', result.raw)
                if all_links:
                    self.state.image_generation_output = {"url": all_links[0].strip('()[]{},. ')}
                    print(f"🖼️ Potential Image URL found (no extension): {all_links[0]}")

    @listen("emergency")
    async def handle_emergency(self):
        print("🚨 Emergency Path Triggered!")
        emergency_text = (
            "🚨 *URGENT WARNING FROM POWERPULSE AI* 🚨\n\n"
            "Dangerous electrical condition detected!\n"
            "1. SHUT OFF the main circuit breaker immediately.\n"
            "2. Evacuate the area.\n"
            "3. Contact emergency services or a certified electrician."
        )
        self.state.text_generation_output = {"text": emergency_text}

    @listen(or_(run_power_pulse_crew, handle_emergency))
    def finalize_and_dispatch(self):
        print("📤 Database Persistence & Final Dispatching...")
        
        final_text = self.state.text_generation_output.get("text", "")
        final_image = self.state.image_generation_output.get("url") if self.state.image_generation_output else None
        to_number = self.state.whatsapp_to or settings.TWILIO_WHATSAPP_TO

        try:
            clean_phone = to_number.replace("whatsapp:", "").strip()
            
            consumer, created = EnergyConsumer.objects.get_or_create(
                phone_number=clean_phone,
                defaults={'average_consumption': 0.0} 
            )

            new_ticket_id = f"TIC-{uuid.uuid4().hex[:6].upper()}"
            
            ticket = ServiceTicket.objects.create(
                consumer=consumer,
                ticket_id=new_ticket_id,
                issue_description=self.state.user_query,
                category=self.state.planner_output.get('category', 'energy_advice'),
                urgency='high' if self.state.planner_output.get('category') == 'emergency' else 'low',
                status='open'
            )

            GeneratedEnergyContent.objects.create(
                ticket=ticket,
                prompt_used=self.state.user_query,
                generated_text=final_text,
                image_url=final_image
            )
            print(f"💾 Record created: Ticket {new_ticket_id} for {clean_phone}")
            
            final_text = f"*Ref ID: {new_ticket_id}*\n\n{final_text}"

        except Exception as e:
            print(f"⚠️ Database Error: {e}")
            pass

        self.state.final_output = {
            "text": final_text,
            "image": final_image
        }

        sid = send_energy_update_to_whatsapp(
            to=to_number,
            text=final_text,
            image_url=final_image
        )
        
        self.state.whatsapp_send_output = [f"Sent: {sid}" if sid else "Failed"]
        print(f"✅ Flow Finished. Response sent to {to_number}")
        
        return self.state.final_output

    async def kickoff_async(self, user_query: str, whatsapp_to: str = None):
        self.state.user_query = user_query
        self.state.whatsapp_to = whatsapp_to
        return await super().kickoff_async()