import asyncio
from datetime import datetime

async def continuous_collision_monitor(fusion_func, object_ids, interval=10):
    """
    Background loop that checks for conjunctions every 'interval' seconds.
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring service started...")
    while True:
        for oid in object_ids:
            # Trigger the fusion/analysis logic
            result = await fusion_func(oid)
            
            if result.get("risk_count", 0) > 0:
                print(f"\n[!!!] CRITICAL ALERT: Object {oid} has {result['risk_count']} conjunction risks!")
                for risk in result['conjunction_risks']:
                    print(f"      -> Threat: {risk['debris_id']} | Distance: {risk['distance_km']:.2f} km")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Object {oid}: Nominal. No risks detected.")
        
        await asyncio.sleep(interval)
