import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime

from .catalog import get_active_catalog
from .propagator import propagate_tle

def generate_indian_orbits_plot() -> bytes:
    catalog = get_active_catalog(limit=300)
    dt = datetime.utcnow()
    
    fig = plt.figure(figsize=(12, 9), facecolor='black')
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('black')
    
    indian_x, indian_y, indian_z = [], [], []
    other_x, other_y, other_z = [], [], []
    
    for sat in catalog:
        try:
            result = propagate_tle(sat["line1"], sat["line2"], dt)
            pos = result["position_eci_km"]
            if sat["is_indian"]:
                indian_x.append(pos[0])
                indian_y.append(pos[1])
                indian_z.append(pos[2])
            else:
                other_x.append(pos[0])
                other_y.append(pos[1])
                other_z.append(pos[2])
        except:
            continue
    
    ax.scatter(other_x, other_y, other_z, c='gray', s=8, alpha=0.6, label='Other Satellites')
    ax.scatter(indian_x, indian_y, indian_z, c='lime', s=80, label='Indian Sovereign Assets 🇮🇳', edgecolors='white', linewidth=0.5)
    
    ax.set_xlabel('X ECI (km)', color='white')
    ax.set_ylabel('Y ECI (km)', color='white')
    ax.set_zlabel('Z ECI (km)', color='white')
    ax.tick_params(colors='white')
    ax.set_title(f'KoshaTrack Tier-Zero Live Orbit View\n{dt.isoformat()}Z | Mumbai Command Center 🇮🇳', color='white', fontsize=14)
    ax.legend(loc='upper left', labelcolor='white')
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    buf.seek(0)
    return buf.read()
