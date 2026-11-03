# Routecraft | Vehicle Route Optimization with ACO

[![Project](https://img.shields.io/badge/project-Experiment%209%20%2F%20Project%205-111111)](#project)
[![Algorithm](https://img.shields.io/badge/algorithm-Ant%20Colony%20Optimization-111111)](#method)
[![Python](https://img.shields.io/badge/Python-3.10%2B-111111)](#run-locally)
[![Data](https://img.shields.io/badge/data-synthetic-lightgrey)](#guardrails)
[![Deploy](https://img.shields.io/badge/deployment-Vercel-111111)](#deployment)

**Experiment 9 mini project for Nature-Inspired Computing (NIC Lab)**  
**Selected topic:** Project 5, Vehicle Route Optimization Using Ant Colony Optimization (ACO)  
**Team:** Hardik Hinduja (20), Avinash Gehi (11), Sahil Deshmukh (9), Siddharth Dey (10)

Routecraft compares pheromone-guided ACO with a random-tour baseline, nearest-neighbor construction, and exact enumeration. The static website presents the synthetic tour as an interactive monochrome 3D scene.

> Every location and coordinate in this project is synthetic and illustrative. Distances are Euclidean coordinate distances, not road-network directions or navigation advice.

## Project links

| Resource | Link |
| --- | --- |
| Live website | [Routecraft production deployment](https://nia-dist.vercel.app/) (checked; HTTP 200, page title `Routecraft | ACO Vehicle Route Optimizer`). |
| Google Colab | [Open the project notebook](https://colab.research.google.com/drive/1GxqpVK-q_ZGQ7XSdVVrjEuHLYpR0fctJ) |
| GitHub | [Hardik182005/NIA](https://github.com/Hardik182005/NIA) |
| Project prompt | [`PROJECT_PROMPT.md`](PROJECT_PROMPT.md) |

## Problem and model

Find a short closed tour that starts at a depot, visits each of nine delivery stops exactly once, then returns to the depot. A fixed ten-node synthetic coordinate set forms a complete Euclidean distance matrix. The primary objective is total route distance.

ACO parameters: 48 ants, 160 iterations, pheromone influence alpha = 1, distance influence beta = 4, evaporation = 0.42, deposit = 100, seed = 141. Every constructed route receives a 2-opt local improvement before pheromone updates.

## Results

The optimizer and exact enumerator both return **31.154 illustrative km** for this seeded instance. The result table is reproducible with `scripts/route_optimizer.py`.

| Method | Route distance (km) | Gap to exact | Notes |
| --- | ---: | ---: | --- |
| Random tours (mean of 500) | 53.455 | 71.587% | Seed 17 |
| Nearest neighbor | 43.401 | 39.313% | Greedy nearest unvisited stop |
| ACO + 2-opt | 31.154 | 0.000% | 48 ants, 160 iterations |
| Exact enumeration | 31.154 | 0.000% | All 9! stop orders |

Equal ACO and exact distances on this particular synthetic instance do not guarantee that ACO finds the global optimum on other problems.

## Files

| File | Purpose |
| --- | --- |
| `scripts/route_optimizer.py` | Synthetic instance, baselines, ACO, exact enumeration, and independent route audit |
| `notebooks/NIA_Vehicle_Route_ACO.ipynb` | Runnable Colab notebook with detailed tables and CSV exports |
| `site/dist/` | Responsive monochrome website with interactive 3D route and ACO simulator |
| `reports/` | Four individual monochrome report PDFs with covers and detailed tables |
| `reports/website_hero.png`, `reports/website_results.png` | Website visual evidence |

## Run locally

```bash
python scripts/route_optimizer.py
python -m http.server 8765 --directory site/dist
```

Open `http://localhost:8765`, drag over the 3D view to orbit it, and select **Run ACO** to refresh the route table.

The notebook writes `route_benchmark_results.csv`, `optimized_route_legs.csv`, `synthetic_locations.csv`, `pairwise_distance_matrix.csv`, `aco_convergence_summary.csv`, and `route_guardrail_audit.csv` in the Colab runtime.

## Deployment

The static site is deployed to production at [https://nia-dist.vercel.app/](https://nia-dist.vercel.app/). The production URL was checked successfully: it returned HTTP 200 and the expected Routecraft page title. The reports include screenshots of the monochrome 3D website.

## Guardrails

- Use synthetic illustrative coordinates only. Do not paste private addresses, customer identities, or delivery telemetry into this demo.
- A route starts and ends at the depot and visits every synthetic stop exactly once.
- The independent audit recomputes route distance from the listed legs and checks completeness before results are presented.
- Exact enumeration provides a lower-bound comparison only for this small nine-stop example.
- The model omits real road networks, traffic, vehicle capacity, time windows, driver hours, costs, and safety constraints. It is not ready for operational dispatch.

## Individual reports

| Student | Roll no. | Report |
| --- | ---: | --- |
| Hardik Hinduja | 20 | `reports/Hardik_Hinduja_20_Vehicle_Route_ACO_Report.pdf` |
| Avinash Gehi | 11 | `reports/Avinash_Gehi_11_Vehicle_Route_ACO_Report.pdf` |
| Sahil Deshmukh | 9 | `reports/Sahil_Deshmukh_9_Vehicle_Route_ACO_Report.pdf` |
| Siddharth Dey | 10 | `reports/Siddharth_Dey_10_Vehicle_Route_ACO_Report.pdf` |

## Team

| Roll no. | Student | Contribution area |
| ---: | --- | --- |
| 20 | Hardik Hinduja | Project coordination and interface |
| 11 | Avinash Gehi | ACO implementation |
| 9 | Sahil Deshmukh | Synthetic instance and benchmark |
| 10 | Siddharth Dey | Results, visualization, and report |

Prepared for Experiment 9 in the Department of Artificial Intelligence and Data Science, Vivekanand Education Society's Institute of Technology.

