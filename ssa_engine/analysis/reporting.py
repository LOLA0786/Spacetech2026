import json
from datetime import datetime

class MissionReporter:
    @staticmethod
    def generate_summary(fused_data):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        obj_id = fused_data['fused_state']['object_id']
        risk_status = "CRITICAL" if fused_data['risk_count'] > 0 else "NOMINAL"
        
        report = f"""
        ========================================
        SPACE SITUATIONAL AWARENESS REPORT
        Generated: {timestamp}
        ========================================
        OBJECT ID: {obj_id}
        STATUS   : {risk_status}
        ----------------------------------------
        CURRENT POSITION (KM):
        X: {fused_data['fused_state']['position']['x']:.2f}
        Y: {fused_data['fused_state']['position']['y']:.2f}
        Z: {fused_data['fused_state']['position']['z']:.2f}
        
        PREDICTED (T+30m):
        X: {fused_data['prediction_30m']['x']:.2f}
        Y: {fused_data['prediction_30m']['y']:.2f}
        Z: {fused_data['prediction_30m']['z']:.2f}
        ----------------------------------------
        RISK ASSESSMENT:
        Total Threats Detected: {fused_data['risk_count']}
        """
        return report

