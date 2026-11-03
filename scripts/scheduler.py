"""Reproducible discrete PSO exam scheduler used in the Colab report."""
from __future__ import annotations

import math
import random
import time
from typing import Any


def generate_instance(seed: int = 42, students: int = 120, exams: int = 12):
    """Create a clearly synthetic student-to-exam registration sample."""
    rng = random.Random(seed)
    records: list[list[int]] = []
    for student in range(students):
        # Three synthetic cohorts each take courses from their own four-exam
        # block, keeping the conflict graph sparse and the demo timetable feasible.
        cohort_count = 3
        cohort_size = math.ceil(students / cohort_count)
        cohort = min(student // cohort_size, cohort_count - 1)
        block_start = cohort * (exams // cohort_count)
        courses = list(range(block_start, min(block_start + exams // cohort_count, exams)))
        rng.shuffle(courses)
        load = min(len(courses), 3 + (student % 4 == 0))
        records.append(sorted(courses[:load]))
    sizes = [sum(exam in row for row in records) for exam in range(exams)]
    weights = [[0] * exams for _ in range(exams)]
    for row in records:
        for i, left in enumerate(row):
            for right in row[i + 1:]:
                weights[left][right] += 1
                weights[right][left] += 1
    return records, sizes, weights


def conflict_count(plan: list[int], weights: list[list[int]]) -> int:
    return sum(weights[a][b] for a in range(len(plan)) for b in range(a + 1, len(plan))
               if plan[a] == plan[b])


def evaluate(plan: list[int], weights: list[list[int]], periods: int) -> dict[str, Any]:
    clashes = conflict_count(plan, weights)
    loads = [plan.count(period) for period in range(periods)]
    occupied = [load for load in loads if load]
    spread = math.sqrt(sum((load - sum(occupied) / len(occupied)) ** 2 for load in occupied)
                       / len(occupied)) if occupied else 0.0
    return {"plan": plan[:], "clashes": clashes, "periods_used": len(occupied),
            "load_spread": spread, "loads": loads,
            "fitness": clashes * 10_000 + len(occupied) * 100 + spread}


def decode_repair(position: list[float], weights: list[list[int]], periods: int) -> list[int]:
    """Decode a particle, placing high-conflict exams first and repairing clashes."""
    exams = len(position)
    degree = [sum(row) for row in weights]
    order = sorted(range(exams), key=lambda e: (-degree[e], position[e], e))
    plan = [-1] * exams
    loads = [0] * periods
    for exam in order:
        choices = []
        for period in range(periods):
            clash_cost = sum(weights[exam][other] for other in range(exams)
                             if plan[other] == period)
            score = (clash_cost * 10_000 + (20 if not loads[period] else 0)
                     + loads[period] * 3 + abs(period - round(position[exam])) * 0.02)
            choices.append((score, period))
        chosen = min(choices)[1]
        plan[exam] = chosen
        loads[chosen] += 1
    return plan


def optimize_pso(weights: list[list[int]], periods: int = 8, seed: int = 141,
                 particles: int = 32, iterations: int = 100):
    """PSO over real-valued period preferences with a discrete repair decoder."""
    rng = random.Random(seed)
    dimensions = len(weights)
    swarm = []
    global_best = None
    for _ in range(particles):
        position = [rng.random() * (periods - 1) for _ in range(dimensions)]
        velocity = [0.0] * dimensions
        plan = decode_repair(position, weights, periods)
        fit = evaluate(plan, weights, periods)
        particle = {"position": position, "velocity": velocity,
                    "best_position": position[:], "best_fitness": fit["fitness"]}
        swarm.append(particle)
        if global_best is None or fit["fitness"] < global_best["fitness"]:
            global_best = {**fit, "position": position[:]}

    for _iteration in range(iterations):
        for particle in swarm:
            for d in range(dimensions):
                r1, r2 = rng.random(), rng.random()
                particle["velocity"][d] = (
                    0.68 * particle["velocity"][d]
                    + 1.42 * r1 * (particle["best_position"][d] - particle["position"][d])
                    + 1.42 * r2 * (global_best["position"][d] - particle["position"][d])
                )
                particle["position"][d] = max(0.0, min(periods - 1,
                    particle["position"][d] + particle["velocity"][d]))
            plan = decode_repair(particle["position"], weights, periods)
            fit = evaluate(plan, weights, periods)
            if fit["fitness"] < particle["best_fitness"]:
                particle["best_fitness"] = fit["fitness"]
                particle["best_position"] = particle["position"][:]
            if fit["fitness"] < global_best["fitness"]:
                global_best = {**fit, "position": particle["position"][:]}
    return {**global_best, "particles": particles, "iterations": iterations}


def random_baseline(weights: list[list[int]], periods: int = 8, seed: int = 141):
    rng = random.Random(seed)
    plan = [rng.randrange(periods) for _ in weights]
    return evaluate(plan, weights, periods)


def greedy_baseline(weights: list[list[int]], periods: int = 8):
    dimension = len(weights)
    degree = [sum(row) for row in weights]
    order = sorted(range(dimension), key=lambda e: -degree[e])
    plan = [-1] * dimension
    loads = [0] * periods
    for exam in order:
        scores = []
        for period in range(periods):
            clash_cost = sum(weights[exam][other] for other in range(dimension)
                             if plan[other] == period)
            scores.append((clash_cost * 10_000 + (20 if not loads[period] else 0)
                           + loads[period] * 3, period))
        chosen = min(scores)[1]
        plan[exam] = chosen
        loads[chosen] += 1
    return evaluate(plan, weights, periods)


def run_experiment(seed: int = 42, students: int = 120, exams: int = 12,
                   periods: int = 8, particles: int = 32, iterations: int = 100):
    records, sizes, weights = generate_instance(seed, students, exams)
    results = {"Random assignment": random_baseline(weights, periods),
               "Degree-greedy repair": greedy_baseline(weights, periods),
               "Discrete PSO": optimize_pso(weights, periods, seed + 99, particles, iterations)}
    conflicts = sum(weights[a][b] for a in range(exams) for b in range(a + 1, exams))
    return {"records": records, "sizes": sizes, "weights": weights, "results": results,
            "parameters": {"seed": seed, "students": students, "exams": exams,
                           "periods": periods, "particles": particles, "iterations": iterations,
                           "total_conflict_weight": conflicts}}


def build_schedule_table(result: dict[str, Any], periods: int):
    from datetime import date, timedelta
    start = date(2026, 11, 9)
    plan = result["plan"]
    rows = []
    for exam, period in enumerate(plan):
        day = period // 2
        slot = "09:00-12:00" if period % 2 == 0 else "13:00-16:00"
        rows.append({"Exam": f"EX-{exam + 1:02d}", "Registrations": None,
                     "Date": (start + timedelta(days=day)).isoformat(),
                     "Session": slot, "Period": period + 1})
    return rows
