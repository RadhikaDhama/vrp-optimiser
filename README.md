# 🚚 Last-Mile Logistics Optimizer (VRP)

A simulation tool to optimize delivery routes under vehicle capacity constraints using heuristic algorithms.

## 🧠 Problem
Efficiently assign delivery points to multiple vehicles while minimizing total travel distance and respecting capacity constraints.

## ⚙️ Approach
- Greedy Nearest Neighbor (baseline)
- 2-opt Local Search (optimization)
- Random Baseline (for benchmarking)

## 🚀 Features
- Multi-vehicle routing (VRP)
- Capacity constraints
- Interactive Streamlit dashboard
- Optimization objective toggle:
  - Minimize Distance
  - Balance Load
  - Minimize Vehicles

## 📊 Results
- Achieved ~25–40% improvement over random baseline
- Demonstrates trade-offs between efficiency and resource utilization

## ▶️ Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🔧 Tech Stack
- Python 3
- NumPy — distance calculations
- Matplotlib — route visualization  
- Streamlit — interactive dashboard

## 🔭 Real-World Extensions
- Time windows per delivery (VRPTW)
- OR-Tools exact solver for small N
- Live GPS coordinates via API
- Multi-depot routing

## 🌐 Live Demo
https://vrp-optimiser-eqbhkzlumt2l2trrqzac4v.streamlit.ap
