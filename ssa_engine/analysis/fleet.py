import asyncio
from datetime import datetime

class FleetMonitor:
    def __init__(self, fuse_endpoint_logic):
        self.fuse_logic = fuse_endpoint_logic

    async def generate_fleet_status(self, active_object_ids):
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_tracked": len(active_object_ids),
            "critical_alerts": [],
            "nominal_objects": []
        }

        for oid in active_object_ids:
            # We call the fusion/analysis logic for each object
            res = await self.fuse_logic(oid)
            
            summary = {
                "object_id": oid,
                "risk_count": len(res.get("risks", [])),
                "has_maneuver_plan": res.get("maneuver_plan") is not None
            }

            if summary["risk_count"] > 0:
                report["critical_alerts"].append(summary)
            else:
                report["nominal_objects"].append(summary)

        return report
