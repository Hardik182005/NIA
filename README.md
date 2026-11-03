# Orbit Exam Timetable Optimizer

[![Project](https://img.shields.io/badge/project-NIC%20Mini--Project-111111)](#)
[![Algorithm](https://img.shields.io/badge/algorithm-Discrete%20PSO-555555)](#method)
[![Python](https://img.shields.io/badge/Python-3.10%2B-111111)](#colab-notebook)
[![License](https://img.shields.io/badge/license-Educational-lightgrey)](#scope-and-guardrails)
[![Deployment](https://img.shields.io/badge/deployment-status%20to%20be%20verified-999999)](#deployment)

**Experiment 9 mini project for Nature-Inspired Computing (NIC Lab)**  
**Topic:** Examination Timetable Scheduling Using Particle Swarm Optimization (PSO)  
**Course:** D16 AD A/B  
**Team:** Hardik Hinduja (Roll 20), Avinash Gehi (Roll 11), Sahil Deshmukh (Roll 9), Siddharth Dey (Roll 10)

Orbit demonstrates how a discrete particle swarm can place examinations into periods while reducing conflicts between exams taken by the same student. The project includes a runnable Google Colab notebook, a small browser-based optimizer, an interactive 3D timetable visualization, detailed result tables, and four student-specific PDF reports.

> All benchmark data in this project is synthetically generated. Results do not represent an institutional student registry or timetable.

## Project links

| Resource | Link |
| --- | --- |
| Live website | To be added after a verified deployment |
| Google Colab notebook | [Open the project notebook](https://colab.research.google.com/drive/1GxqpVK-q_ZGQ7XSdVVrjEuHLYpR0fctJ) |
| GitHub repository | [Hardik182005/NIA](https://github.com/Hardik182005/NIA) |

## What is included

| Path | Purpose |
| --- | --- |
| `notebooks/NIA_Exam_Timetable_PSO.ipynb` | Self-contained Colab notebook with PSO, audit checks, result tables, monochrome plot, and CSV exports |
| `scripts/scheduler.py` | Reusable synthetic-data generator, conflict graph, decoder, baselines, and PSO implementation |
| `site/dist/` | Responsive black-on-white website and working 3D/PSO demo |
| `reports/` | Four monochrome PDF reports with individualized cover pages |
| `PROJECT_PROMPT.md` | Prompt used to define the implementation and guardrails |

## Problem formulation

Each exam is assigned to exactly one of eight available periods. For every pair of exams, the conflict graph stores how many students are registered in both. The primary objective is to reduce weighted simultaneous-exam conflicts. The secondary objective uses fewer periods and balances their loads.

The benchmark instance contains 120 synthetic students and 12 exams. Students belong to one of three cohorts and take three or four exams from that cohort's four-exam block. This produces a feasible conflict graph with a clear zero-clash target while keeping the test reproducible.

Fitness is calculated as:

```text
fitness = student_clash_pairs × 10,000 + periods_used × 100 + load_spread
```

The PSO uses 32 particles, 100 iterations, inertia 0.68, and cognitive/social coefficients 1.42. Particles hold continuous period preferences; a degree-ordered discrete decoder repairs each candidate assignment.

## Result tables

The notebook produces:

- parameter and synthetic data summary
- random, degree-greedy, and PSO benchmark comparison
- optimized timetable and period load tables
- anonymous synthetic registration sample
- symmetric exam-conflict weight matrix
- independent guardrail audit
- CSV exports for benchmark results, timetable, sample registrations, conflict matrix, and audit

Reference deterministic objective results (seed 42, Python implementation):

| Method | Student clash pairs | Periods used | Feasible |
| --- | ---: | ---: | --- |
| Random assignment | 51 | 7 | No |
| Degree-greedy repair | 0 | 4 | Yes |
| Discrete PSO | 0 | 4 | Yes |

Runtime varies by machine; the notebook measures it during each run. The PSO and greedy decoder reach the same hard-constraint optimum on this small synthetic instance, so this result does not establish PSO superiority over the greedy baseline.

## Run locally

Requirements: Python 3.10+, pandas, and matplotlib for the notebook tables and plot.

```bash
python -m pip install pandas matplotlib
python -m pip install jupyter
jupyter notebook notebooks/NIA_Exam_Timetable_PSO.ipynb
```

To run the optimizer module without notebook dependencies:

```bash
python -c "from scripts.scheduler import run_experiment; r=run_experiment(); print({k:(v['clashes'],v['periods_used']) for k,v in r['results'].items()})"
```

To preview the website:

```bash
python -m http.server 8765 --directory site/dist
```

Then open `http://localhost:8765` and choose **Run PSO**. Drag across the 3D scene to orbit the timetable model.

## Deployment

The static site is deployable on Vercel from `site/dist`. In Vercel, import this repository and set the project root to `site/dist`, framework preset to **Other**, and build command to none. The production URL will be recorded here only after deployment is confirmed.

The static site can be deployed from the `site/dist` directory. Deployment status and production URL are recorded here after publication is verified. Do not commit or publish access tokens.

## Scope and guardrails

- Only synthetic student registrations are used. Never upload identifiable student records to this demonstration.
- Each exam must be scheduled exactly once, every period index must be within the declared horizon, and the final schedule is independently audited against individual student exam pairs.
- A zero-clash result is stated only if the audit returns zero.
- The model does not include room capacities, invigilators, accessibility, course precedence, exam duration variation, or institutional rules.
- PSO is stochastic in general and heuristic. Reproducible output on this instance is not proof of global optimality or operational readiness.
- Any real timetable requires validation by its data owner and academic administrators before use.

## Team

| Roll no. | Student | Contribution area |
| ---: | --- | --- |
| 20 | Hardik Hinduja | Project coordination and interface |
| 11 | Avinash Gehi | PSO and implementation |
| 9 | Sahil Deshmukh | Synthetic instance and evaluation |
| 10 | Siddharth Dey | Results, visualization, and report |

## Acknowledgment

Prepared for the Experiment 9 mini project in the Department of Artificial Intelligence and Data Science, Vivekanand Education Society's Institute of Technology.
