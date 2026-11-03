"""Synthetic delivery-route benchmark solved with Ant Colony Optimization."""
from __future__ import annotations
import itertools
import math
import random
import time

LOCATIONS = [
    {"id": "DEPOT", "name": "VESIT Depot", "x": 0.0, "y": 0.0},
    {"id": "STOP-01", "name": "Harbour Point", "x": 2.4, "y": 1.8},
    {"id": "STOP-02", "name": "Cedar Market", "x": 4.7, "y": 0.9},
    {"id": "STOP-03", "name": "North Arcade", "x": 5.6, "y": 3.5},
    {"id": "STOP-04", "name": "Lakeview Hub", "x": 3.9, "y": 5.2},
    {"id": "STOP-05", "name": "Garden Square", "x": 1.1, "y": 4.8},
    {"id": "STOP-06", "name": "East Works", "x": 7.4, "y": 5.9},
    {"id": "STOP-07", "name": "Riverside Depot", "x": 8.2, "y": 2.6},
    {"id": "STOP-08", "name": "Hillcrest Store", "x": 6.3, "y": -1.4},
    {"id": "STOP-09", "name": "South Exchange", "x": -1.8, "y": 2.7},
]


def make_distance_matrix(locations=LOCATIONS):
    return [[math.hypot(a["x"] - b["x"], a["y"] - b["y"])
             for b in locations] for a in locations]


def route_distance(route, distances):
    return sum(distances[route[i]][route[i + 1]] for i in range(len(route) - 1))


def valid_route(route, node_count):
    return (len(route) == node_count + 1 and route[0] == 0 and route[-1] == 0
            and sorted(route[1:-1]) == list(range(1, node_count)))


def nearest_neighbor(distances):
    route = [0]
    remaining = set(range(1, len(distances)))
    while remaining:
        current = route[-1]
        nxt = min(remaining, key=lambda node: (distances[current][node], node))
        route.append(nxt)
        remaining.remove(nxt)
    route.append(0)
    return {"route": route, "distance": route_distance(route, distances)}


def random_baseline(distances, seed=17, trials=500):
    rng = random.Random(seed)
    nodes = list(range(1, len(distances)))
    candidates = []
    for _ in range(trials):
        rng.shuffle(nodes)
        route = [0, *nodes, 0]
        candidates.append(route_distance(route, distances))
    return {"route": None, "distance": sum(candidates) / len(candidates),
            "best_distance": min(candidates), "trials": trials}


def exact_optimum(distances):
    best_distance = math.inf
    best_route = None
    for order in itertools.permutations(range(1, len(distances))):
        route = (0, *order, 0)
        length = route_distance(route, distances)
        if length < best_distance:
            best_distance, best_route = length, list(route)
    return {"route": best_route, "distance": best_distance}


def two_opt(route, distances):
    best = route[:]
    improved = True
    while improved:
        improved = False
        for left in range(1, len(best) - 2):
            for right in range(left + 1, len(best) - 1):
                candidate = best[:left] + list(reversed(best[left:right + 1])) + best[right + 1:]
                if route_distance(candidate, distances) + 1e-12 < route_distance(best, distances):
                    best, improved = candidate, True
    return best


def ant_colony(distances, seed=141, ants=48, iterations=160,
               alpha=1.0, beta=4.0, evaporation=0.42, deposit=100.0):
    """ACO with roulette-wheel transitions, elitist pheromone and 2-opt."""
    rng = random.Random(seed)
    n = len(distances)
    pheromone = [[1.0 for _ in range(n)] for _ in range(n)]
    eta = [[0.0 if i == j else 1.0 / max(distances[i][j], 1e-9)
            for j in range(n)] for i in range(n)]
    best_route = None
    best_length = math.inf
    history = []
    for _ in range(iterations):
        iteration_best_route, iteration_best_length = None, math.inf
        for _ant in range(ants):
            route, remaining = [0], set(range(1, n))
            while remaining:
                current = route[-1]
                options = sorted(remaining)
                weights = [(pheromone[current][node] ** alpha) * (eta[current][node] ** beta)
                           for node in options]
                pick = rng.random() * sum(weights)
                chosen = options[-1]
                for node, weight in zip(options, weights):
                    pick -= weight
                    if pick <= 0:
                        chosen = node
                        break
                route.append(chosen)
                remaining.remove(chosen)
            route.append(0)
            route = two_opt(route, distances)
            length = route_distance(route, distances)
            if length < iteration_best_length:
                iteration_best_route, iteration_best_length = route, length
            if length < best_length:
                best_route, best_length = route[:], length
        for i in range(n):
            for j in range(n):
                pheromone[i][j] = max(1e-8, pheromone[i][j] * (1 - evaporation))
        for route, length, amount in [(iteration_best_route, iteration_best_length, 1.0),
                                      (best_route, best_length, 2.0)]:
            for left, right in zip(route, route[1:]):
                pheromone[left][right] += amount * deposit / length
                pheromone[right][left] += amount * deposit / length
        history.append(best_length)
    return {"route": best_route, "distance": best_length, "history": history,
            "ants": ants, "iterations": iterations, "alpha": alpha, "beta": beta,
            "evaporation": evaporation, "seed": seed}


def independent_audit(route, distances, node_count):
    valid = valid_route(route, node_count)
    measured = route_distance(route, distances) if valid else math.inf
    return {"closed_route_starts_and_ends_at_depot": valid and route[0] == route[-1] == 0,
            "each_delivery_stop_visited_once": valid and len(set(route[1:-1])) == node_count - 1,
            "all_nodes_included": valid and set(route[1:-1]) == set(range(1, node_count)),
            "distance_recomputed_from_legs": measured,
            "route_is_valid": valid}


def run_experiment():
    distances = make_distance_matrix()
    timings = {}
    start = time.perf_counter(); random_result = random_baseline(distances); timings["Random (500 tours)"] = time.perf_counter() - start
    start = time.perf_counter(); nearest = nearest_neighbor(distances); timings["Nearest neighbor"] = time.perf_counter() - start
    start = time.perf_counter(); aco = ant_colony(distances); timings["ACO + 2-opt"] = time.perf_counter() - start
    start = time.perf_counter(); exact = exact_optimum(distances); timings["Exact enumeration"] = time.perf_counter() - start
    results = {"Random (500 tours)": random_result, "Nearest neighbor": nearest,
               "ACO + 2-opt": aco, "Exact enumeration": exact}
    for name, result in results.items():
        if name == "Random (500 tours)":
            result["runtime_seconds"] = timings[name]
        else:
            result["runtime_seconds"] = timings[name]
    audit = independent_audit(aco["route"], distances, len(LOCATIONS))
    audit["distance_matches_optimizer"] = math.isclose(audit["distance_recomputed_from_legs"], aco["distance"], rel_tol=0, abs_tol=1e-9)
    audit["gap_to_exact_percent"] = (aco["distance"] / exact["distance"] - 1) * 100
    return {"locations": LOCATIONS, "distances": distances, "results": results,
            "audit": audit}


if __name__ == "__main__":
    r = run_experiment()
    for name, result in r["results"].items():
        score = result.get("distance", result.get("best_distance"))
        print(f"{name}: {score:.3f} km")
    print("Audit:", r["audit"])
