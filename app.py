import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from vrp import run_vrp

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="VRP Optimizer",
    page_icon="🚚",
    layout="wide"
)

st.title("🚚 Multi-Vehicle Route Optimizer (VRP)")
st.markdown("""
###  What I built
This project simulates how delivery companies assign orders to vehicles under capacity constraints.

Instead of exact optimization (which is expensive), I used heuristics + local search
to generate fast, scalable, near-optimal routing solutions.
""")

# ── Sidebar controls ─────────────────────────────────────────────
st.sidebar.header("⚙️ Problem Parameters")

n_points   = st.sidebar.slider("Number of Delivery Points", 10, 40, 20)
n_vehicles = st.sidebar.slider("Number of Vehicles",         2,  8,  4)
capacity   = st.sidebar.slider("Vehicle Capacity",          20, 80, 40)
seed       = st.sidebar.slider("Random Seed",                1, 100, 42)
objective = st.sidebar.selectbox(
    "Optimization Objective",
    ["Minimize Distance", "Balance Load", "Minimize Vehicles"]

)
st.sidebar.markdown("---")
st.sidebar.markdown("**How it works:**")
st.sidebar.markdown("1. Greedy nearest-neighbour assigns stops to vehicles")
st.sidebar.markdown("2. 2-opt local search improves each vehicle's route")
st.sidebar.markdown("3. Constraints: each vehicle cannot exceed capacity")

# ── Run solver ───────────────────────────────────────────────────
with st.spinner("Optimizing routes..."):
    best_result = None

for s in range(5):
    r = run_vrp(n_points, n_vehicles, capacity, seed+s, objective)
    if best_result is None or r["opt_dist"] < best_result["opt_dist"]:
        best_result = r

result = best_result
points    = result["points"]
demands   = result["demands"]
colors    = plt.cm.tab10.colors

# ── Top metrics ──────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Random Distance",  f"{result['random_dist']:.1f}")
col2.metric("Optimized Distance", f"{result['opt_dist']:.1f}")
col3.metric("Improvement",        f"{result['improvement']:.1f}%", delta=f"-{result['improvement']:.1f}%")
col4.metric("Vehicles Used",      f"{result['n_vehicles']}")

st.markdown("---")
st.markdown("###  Key Insights")

unused = sum(1 for r in result["opt_routes"] if len(r) == 0)

st.write(f"- {unused} vehicles were unused → possible over-allocation of fleet.")
st.write("- 2-opt improves routes by removing path inefficiencies (local swaps).")
st.write(f"- Optimization objective used: **{objective}**")

# ── Route plots ───────────────────────────────────────────────────
def draw_routes(ax, routes, points, demands, colors, title):
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.scatter(points[1:, 0], points[1:, 1],
               c='steelblue', s=60, zorder=3)

    # Label demand on each point
    for i in range(1, len(points)):
        ax.annotate(f"d={demands[i]}",
                    (points[i, 0], points[i, 1]),
                    textcoords="offset points",
                    xytext=(5, 5), fontsize=7, color='gray')

    # Draw warehouse
    ax.scatter(points[0, 0], points[0, 1],
               c='red', s=200, marker='*', zorder=5, label='Warehouse')

    # Draw each vehicle route
    legend_patches = []
    for v, route in enumerate(routes):
        if not route:
            continue
        c = colors[v % len(colors)]
        full_route = [0] + route + [0]
        xs = [points[i, 0] for i in full_route]
        ys = [points[i, 1] for i in full_route]
        ax.plot(xs, ys, color=c, linewidth=1.8,
                alpha=0.8, marker='o', markersize=5)
        legend_patches.append(
            mpatches.Patch(color=c, label=f"Vehicle {v+1}")
        )

    ax.legend(handles=legend_patches, fontsize=8, loc='upper right')
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)


fig, axes = plt.subplots(1, 2, figsize=(14, 6))
draw_routes(axes[0], result["baseline_routes"], points, demands,
            colors, f"Baseline (Greedy)\nTotal Dist: {result['baseline_dist']:.1f}")
draw_routes(axes[1], result["opt_routes"],      points, demands,
            colors, f"Optimized (2-opt)\nTotal Dist: {result['opt_dist']:.1f}")

plt.tight_layout()
st.pyplot(fig)

# ── Per-vehicle breakdown table ───────────────────────────────────
st.markdown("---")
st.subheader("📊 Vehicle Utilization Breakdown")

util = result["utilization"]
table_data = {
    "Vehicle"         : [f"Vehicle {i+1}" for i in range(result["n_vehicles"])],
    "Stops Assigned"  : [len(r) for r in result["opt_routes"]],
    "Load Used"       : [sum(demands[i] for i in r) for r in result["opt_routes"]],
    "Capacity"        : [capacity] * result["n_vehicles"],
    "Utilization %"   : util,
    "Route Distance"  : [round(
                            __import__('vrp').route_distance(r, points), 1
                         ) for r in result["opt_routes"]],
}

st.dataframe(table_data, use_container_width=True)

# ── Utilization bar chart ─────────────────────────────────────────
st.subheader("🔋 Capacity Utilization per Vehicle")
fig2, ax2 = plt.subplots(figsize=(8, 3))
bars = ax2.bar(
    [f"V{i+1}" for i in range(len(util))],
    util,
    color=[colors[i % len(colors)] for i in range(len(util))]
)
ax2.axhline(100, color='red', linestyle='--', linewidth=1, label='Max Capacity')
ax2.set_ylabel("Utilization %")
ax2.set_ylim(0, 120)
ax2.legend()
for bar, val in zip(bars, util):
    ax2.text(bar.get_x() + bar.get_width()/2,
             bar.get_height() + 2,
             f"{val}%", ha='center', fontsize=9)
st.pyplot(fig2)

# ── Footer ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("Built with Python · NumPy · Matplotlib · Streamlit")