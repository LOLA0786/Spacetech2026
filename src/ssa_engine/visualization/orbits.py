import numpy as np
import plotly.graph_objects as go
from plotly.offline import plot

def plot_3d_orbits(states_list, labels, earth_texture=True, conjunction_ellipsoids=None):
    """
    states_list: list of position arrays (N x 3)
    conjunction_ellipsoids: optional list of (center, cov) for 3σ ellipsoids
    """
    fig = go.Figure()

    # Earth
    if earth_texture:
        fig.add_trace(go.Surface(
            z=[[0,0],[0,0]], x=[[0,1],[0,1]], y=[[0,0],[1,1]],
            surfacecolor=np.ones((2,2)), showscale=False, opacity=0.8))

    colors = ['red', 'blue', 'green', 'orange', 'purple']
    for i, pos in enumerate(states_list):
        fig.add_trace(go.Scatter3d(
            x=pos[:,0]/1e6, y=pos[:,1]/1e6, z=pos[:,2]/1e6,
            mode='lines', name=labels[i], line=dict(color=colors[i % len(colors)], width=6)))

    # Optional covariance ellipsoids
    if conjunction_ellipsoids:
        for center, cov in conjunction_ellipsoids:
            # Simplified 3σ sphere for demo
            u = np.linspace(0, 2*np.pi, 20)
            v = np.linspace(0, np.pi, 20)
            r = 3 * np.sqrt(np.trace(cov[:3,:3])/3) / 1e6
            x = center[0]/1e6 + r * np.outer(np.cos(u), np.sin(v))
            y = center[1]/1e6 + r * np.outer(np.sin(u), np.sin(v))
            z = center[2]/1e6 + r * np.outer(np.zeros_like(u), np.cos(v))
            fig.add_trace(go.Surface(x=x, y=y, z=z, opacity=0.3))

    fig.update_layout(scene=dict(xaxis_title='X (Mm)', yaxis_title='Y (Mm)', zaxis_title='Z (Mm)',
                                 aspectmode='data'),
                      title="KoshaTrack 3D Orbit Visualization")
    plot(fig, filename='orbit_viz.html', auto_open=False)
    print("Saved interactive HTML: orbit_viz.html")
