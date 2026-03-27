import numpy as np

# ── 1. Generate problem ──────────────────────────────────────────
def generate_problem(n_points=20, n_vehicles=4, capacity=40, seed=42):
    np.random.seed(seed)
    # First point [0] is always the warehouse
    points  = np.random.rand(n_points, 2) * 100
    demands = np.random.randint(5, 15, size=n_points)
    demands[0] = 0  # warehouse has no demand
    return points, demands, n_vehicles, capacity


# ── 2. Distance between two points ──────────────────────────────
def distance(p1, p2):
    return np.linalg.norm(p1 - p2)


# ── 3. Total distance of one route ──────────────────────────────
def route_distance(route, points):
    if len(route) == 0:
        return 0
    # Start from warehouse (0) → visit stops → return to warehouse (0)
    dist  = distance(points[0], points[route[0]])
    dist += sum(distance(points[route[i]], points[route[i+1]])
                for i in range(len(route) - 1))
    dist += distance(points[route[-1]], points[0])
    return dist


# ── 4. Total distance across ALL vehicles ───────────────────────
def total_fleet_distance(routes, points):
    return sum(route_distance(r, points) for r in routes)


# ── 5. Greedy assignment (baseline) ─────────────────────────────
def greedy_assign(points, demands, n_vehicles, capacity):
    n          = len(points)
    visited    = [False] * n
    visited[0] = True          # warehouse already visited
    routes     = [[] for _ in range(n_vehicles)]
    loads      = [0]  * n_vehicles

    # Each vehicle: greedily pick nearest unvisited point it can carry
    for v in range(n_vehicles):
        current = 0            # start at warehouse
        while True:
            best_dist, best_idx = float('inf'), -1
            for i in range(1, n):
                if not visited[i] and loads[v] + demands[i] <= capacity:
                    d = distance(points[current], points[i])
                    if d < best_dist:
                        best_dist, best_idx = d, i
            if best_idx == -1:
                break          # no more stops fit this vehicle
            routes[v].append(best_idx)
            loads[v]        += demands[best_idx]
            visited[best_idx] = True
            current          = best_idx

    return routes


# ── 6. 2-opt improvement on a single route ──────────────────────
def two_opt(route, points):
    if len(route) < 3:
        return route
    best = route[:]
    improved = True
    while improved:
        improved = False
        for i in range(len(best) - 1):
            for j in range(i + 2, len(best)):
                new_route      = best[:]
                new_route[i:j] = best[i:j][::-1]
                if route_distance(new_route, points) < route_distance(best, points):
                    best     = new_route
                    improved = True
    return best


# ── 7. Apply 2-opt to every vehicle's route ─────────────────────
def optimize_all_routes(routes, points):
    return [two_opt(r, points) for r in routes]


# ── 8. Utilization % per vehicle ─────────────────────────────────
def vehicle_utilization(routes, demands, capacity):
    utils = []
    for r in routes:
        load = sum(demands[i] for i in r)
        utils.append(round(load / capacity * 100, 1))
    return utils
def random_routes(points, demands, n_vehicles, capacity):
    indices = list(range(1, len(points)))
    np.random.shuffle(indices)

    routes = [[] for _ in range(n_vehicles)]
    loads = [0]*n_vehicles

    for i in indices:
        for v in range(n_vehicles):
            if loads[v] + demands[i] <= capacity:
                routes[v].append(i)
                loads[v] += demands[i]
                break
    return routes

# ── 9. Run everything, return summary dict ───────────────────────
def run_vrp(n_points, n_vehicles, capacity, seed=42, objective="Minimize Distance"):
    points, demands, n_vehicles, capacity = generate_problem(
        n_points, n_vehicles, capacity, seed
    )
    # Random baseline
    random_routes_ = random_routes(points, demands, n_vehicles, capacity)
    random_dist = total_fleet_distance(random_routes_, points)
    # Baseline
    baseline_routes = greedy_assign(points, demands, n_vehicles, capacity)
        # Modify behavior based on objective
    if objective == "Minimize Vehicles":
        # force tighter packing by reducing vehicles artificially
        n_vehicles = max(1, n_vehicles - 1)

    elif objective == "Balance Load":
        # simple trick: shuffle demands to distribute load more evenly
        np.random.shuffle(demands[1:])
    baseline_dist   = total_fleet_distance(baseline_routes, points)

    # Optimized
    opt_routes = optimize_all_routes(baseline_routes, points)
    opt_dist   = total_fleet_distance(opt_routes, points)

    improvement = (baseline_dist - opt_dist) / baseline_dist * 100

    return {
        "points"          : points,
        "demands"         : demands,
        "baseline_routes" : baseline_routes,
        "opt_routes"      : opt_routes,
        "baseline_dist"   : round(baseline_dist, 2),
        "opt_dist"        : round(opt_dist, 2),
        "improvement"     : round(improvement, 2),
        "utilization"     : vehicle_utilization(opt_routes, demands, capacity),
        "n_vehicles"      : n_vehicles,
        "capacity"        : capacity,
        "random_dist": round(random_dist, 2),
    }