"""
PowerPulse AI - Twilio WhatsApp Sender
Final Optimized Version for HTU Graduation Project
Author: Mohammad Amaierh
"""
from __future__ import annotations
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    _TWILIO_AVAILABLE = True
except ImportError:
    Client = None
    TwilioRestException = None
    _TWILIO_AVAILABLE = False


def get_twilio_client():
   
    sid = settings.TWILIO_ACCOUNT_SID
    token = settings.TWILIO_AUTH_TOKEN
    if not sid or not token:
        raise ValueError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set in settings/.env")
    return Client(sid, token)


def send_energy_update_to_whatsapp(to: str, text: str = "", image_url: str = None) -> str | None:
    
    if not _TWILIO_AVAILABLE:
        logger.error("twilio package not installed. Run: pip install twilio")
        return None

    from_number = settings.TWILIO_WHATSAPP_NUMBER
    if not from_number.startswith("whatsapp:"):
        from_number = f"whatsapp:{from_number}"
    
    if not to.startswith("whatsapp:"):
        to = f"whatsapp:{to}"

    if not text and not image_url:
        logger.warning(f"Skipping send to {to}: No text or image provided.")
        return None

   
    if text and len(text) > 1550:
        logger.warning(f"⚠️ Message body too long ({len(text)} chars). Truncating...")
        text = text[:1550] + "...\n\n(Content shortened to fit WhatsApp limits)"

    final_media_url = None
    if image_url and any(domain in image_url for domain in ["http://", "https://"]):
        if "localhost" not in image_url and "127.0.0.1" not in image_url:
            final_media_url = [image_url]
            logger.info(f"🖼️ Valid image URL detected: {image_url}")
        else:
            logger.warning("⚠️ Localhost image URL detected. Twilio cannot access local files.")

    try:
        client = get_twilio_client()
        
        message_args = {
            "from_": from_number,
            "to": to,
            "body": text or ""
        }
        
        if final_media_url:
            message_args["media_url"] = final_media_url

        resp = client.messages.create(**message_args)
        
        logger.info(f"✅ WhatsApp Sent Successfully! SID: {resp.sid} | Recipient: {to}")
        return resp.sid

    except TwilioRestException as e:
        error_msg = str(e)
        logger.error(f"❌ Twilio API Error: {error_msg} (Code: {e.code})")
        
        if e.code == 21617:
            logger.error("🛑 The message is still too long for Twilio.")
        elif e.code == 63007:
            logger.error("🛑 Error 63007: Invalid WhatsApp sender number.")
            
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected Error during WhatsApp dispatch: {str(e)}")
        return None