"""
WhatsApp SSA Alert Bot using Twilio
"""
from twilio.rest import Client
import os
from datetime import datetime

class WhatsAppSSABot:
    def __init__(self):
        self.client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        self.from_number = 'whatsapp:+14155238886'  # Twilio sandbox
    
    def send_conjunction_alert(self, to_number, satellite_name, 
                                target_name, probability, tta_hours):
        """
        Send collision alert via WhatsApp
        """
        message = f"""
🚨 **KoshaTrack Collision Alert**

Primary: {satellite_name}
Target: {target_name}
Collision Probability: {probability:.2%}
Time to TCA: {tta_hours:.1f} hours

Recommended Action: Review maneuver options
View details: https://koshatrack.space/conjunctions/{conjunction_id}

—KoshaTrack SSA Engine
        """
        
        try:
            msg = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=f'whatsapp:{to_number}'
            )
            return {'status': 'sent', 'sid': msg.sid}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    def send_maneuver_recommendation(self, to_number, satellite, 
                                     delta_v, fuel_cost):
        """
        Send maneuver recommendation
        """
        message = f"""
🛰️ **KoshaTrack Maneuver Advice**

Satellite: {satellite}
Recommended ΔV: {delta_v:.3f} m/s
Fuel Cost: {fuel_cost:.2f} kg
Safe-Dodge Window: Next 6 hours

Execute maneuver? Reply:
✅ YES to confirm
❌ NO to monitor

—KoshaTrack SSA Engine
        """
        
        msg = self.client.messages.create(
            body=message,
            from_=self.from_number,
            to=f'whatsapp:{to_number}'
        )
        return msg.sid

# Test
if __name__ == "__main__":
    bot = WhatsAppSSABot()
    # Test with your number
    result = bot.send_conjunction_alert(
        to_number='+91XXXXXXXXXX',  # Your number
        satellite_name='ISRO-SAT-01',
        target_name='Debris-12345',
        probability=0.0023,
        tta_hours=18.5
    )
    print(f"Alert sent: {result}")
