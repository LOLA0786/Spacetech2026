from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from datetime import datetime

from .screening import screen_conjunctions
from .visualize import generate_indian_orbits_plot

def generate_mod_briefing_pdf() -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph("KoshaTrack Tier-Zero SSA Briefing", styles['Title']))
    story.append(Paragraph(f"Generated: {datetime.utcnow().isoformat()}Z | Mumbai Command 🇮🇳", styles['Normal']))
    story.append(Spacer(1, 12))
    
    screening = screen_conjunctions()
    story.append(Paragraph("Current Conjunction Risks", styles['Heading1']))
    story.append(Paragraph(f"Indian Assets Monitored: {screening['indian_sovereign_assets_detected']}", styles['Normal']))
    story.append(Paragraph(f"Close Approaches: {screening['total_close_approaches']}", styles['Normal']))
    
    # Table of top risks
    data = [["Asset", "Threat", "Distance (km)", "Risk Level"]]
    for risk in screening['top_risks'][:10]:
        data.append([risk['primary'], risk['secondary'], risk['distance_km'], risk.get('risk_level', 'MONITOR')])
    story.append(Table(data))
    
    # Embed visualization
    plot_bytes = generate_indian_orbits_plot()
    story.append(Image(BytesIO(plot_bytes), width=400, height=300))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.read()
