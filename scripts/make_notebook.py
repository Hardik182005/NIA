"""Create a self-contained Colab notebook from scheduler.py."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
algorithm = (root / "scripts" / "scheduler.py").read_text(encoding="utf-8")

def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}

def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": text.splitlines(keepends=True)}

cells = [
    md("""# Examination Timetable Scheduling Using Particle Swarm Optimization

**Nature-Inspired Computing · Experiment 9 Mini Project**  
**Team:** Hardik Hinduja (20), Avinash Gehi (11), Sahil Deshmukh (9), Siddharth Dey (10)

This self-contained notebook creates a reproducible synthetic examination instance, builds a weighted student-conflict graph, runs a discrete Particle Swarm Optimization (PSO) search with a timetable repair decoder, and reports detailed plain tables. No real student records are used. Run all cells from top to bottom in Google Colab.

**Chosen topic:** Project 2, Examination Timetable Scheduling Using PSO. It has an explicit measurable objective: minimize simultaneous exams taken by the same student, then use fewer periods with balanced loads.

## Guardrails
- Synthetic registrations only; do not paste student names, IDs, grades, or private registration data into this demonstration.
- Every exam is assigned exactly one period within the declared timetable horizon.
- A post-run audit checks student conflicts, exam count, period bounds, and schedule completeness.
- A zero-conflict result is reported only when the independent audit verifies it.
- The fixed seed makes the generated instance and search reproducible; it is not evidence about a real institution's timetable.

## The prompt used to scope the implementation
"Build a complete, reproducible Nature-Inspired Computing mini project for examination timetable scheduling with discrete PSO. Generate a clearly synthetic student-course registration instance; construct a weighted conflict graph; implement standard personal/global-best particle updates plus a deterministic repair decoder; compare PSO with random assignment and a degree-greedy baseline; audit hard constraints and student clashes; display clear monochrome tables for parameters, benchmark metrics, final schedule, per-exam registration totals, sample registrations, and conflict weights; export CSV outputs; explain limitations and privacy guardrails; and provide a minimal black-on-white interactive website with a working 3D schedule visualization. Do not present synthetic results as real institutional data."
"""),
    md("## 1. Imports and reproducibility\nWe use the Python standard library for generation and optimization, plus pandas and matplotlib for readable result tables and a monochrome conflict graph."),
    code("""import math, random, time
from datetime import date, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 140)
"""),
    md("## 2. Complete scheduling implementation\nEncoding: one real-valued period preference per exam. The decoder orders highly constrained exams first, assigns the period with the lowest incremental conflict penalty, then uses load and particle preference as tie-breakers. Fitness is `clashes × 10,000 + occupied periods × 100 + load spread`."),
    code(algorithm),
    md("## 3. Generate one deterministic demonstration instance\nThere are 120 synthetic students, 12 exams and 8 available periods across four days. The students are split into three cohorts of 40; each cohort takes exams from its own four-exam block. Students take three or four exams within their cohort."),
    code("""SEED, STUDENTS, EXAMS, PERIODS = 42, 120, 12, 8
PARTICLES, ITERATIONS = 32, 100
registrations, course_sizes, conflict_weights = generate_instance(SEED, STUDENTS, EXAMS)
parameter_table = pd.DataFrame([
    {'Parameter':'Random seed','Value':SEED,'Meaning':'Reproducible synthetic instance'},
    {'Parameter':'Students','Value':STUDENTS,'Meaning':'Synthetic enrolment records'},
    {'Parameter':'Exams','Value':EXAMS,'Meaning':'Each exam scheduled once'},
    {'Parameter':'Available periods','Value':PERIODS,'Meaning':'Two periods per day across four days'},
    {'Parameter':'Swarm size','Value':PARTICLES,'Meaning':'PSO particles'},
    {'Parameter':'Iterations','Value':ITERATIONS,'Meaning':'PSO update cycles'},
    {'Parameter':'Total registrations','Value':sum(map(len, registrations)),'Meaning':'Synthetic student-exam enrolments'},
])
display(parameter_table)
"""),
    md("## 4. Compare baselines and PSO\nAll methods receive the same registration instance. Random assignment is an intentionally un-repaired baseline. Greedy and PSO schedules pass through a conflict-aware decoder. Wall time varies by runtime; the fixed-seed objective and audit are the primary comparison."),
    code("""timings = {}
t0 = time.perf_counter(); random_result = random_baseline(conflict_weights, PERIODS, SEED + 99); timings['Random assignment'] = time.perf_counter()-t0
t0 = time.perf_counter(); greedy_result = greedy_baseline(conflict_weights, PERIODS); timings['Degree-greedy repair'] = time.perf_counter()-t0
t0 = time.perf_counter(); pso_result = optimize_pso(conflict_weights, PERIODS, SEED + 99, PARTICLES, ITERATIONS); timings['Discrete PSO'] = time.perf_counter()-t0
results = {'Random assignment':random_result,'Degree-greedy repair':greedy_result,'Discrete PSO':pso_result}
rows=[]
for name,result in results.items():
    rows.append({'Method':name,'Student clash pairs':result['clashes'],'Periods used':result['periods_used'],
                 'Load spread':round(result['load_spread'],3),'Fitness':round(result['fitness'],3),
                 'Runtime seconds':round(timings[name],4),'Feasible':result['clashes']==0})
benchmark_table=pd.DataFrame(rows)
display(benchmark_table)
"""),
    md("## 5. Final timetable and period loads\nEach row below assigns one exam exactly once. Day and session are display labels for the eight available periods."),
    code("""best = pso_result
start_date = date(2026, 11, 9)
schedule_rows=[]
for exam, period in enumerate(best['plan']):
    schedule_rows.append({'Exam':f'EX-{exam+1:02d}','Registrations':course_sizes[exam],
        'Day':(start_date+timedelta(days=period//2)).strftime('%A, %d %b %Y'),
        'Session':'09:00-12:00' if period%2==0 else '13:00-16:00','Period':period+1})
schedule_table=pd.DataFrame(schedule_rows).sort_values(['Period','Exam']).reset_index(drop=True)
display(schedule_table)
period_table=(schedule_table.groupby(['Period','Day','Session'],as_index=False)
              .agg(Exams=('Exam','count'),Registrations=('Registrations','sum'))
              .sort_values('Period'))
display(period_table)
"""),
    md("## 6. Data and conflict detail\nThe sample below intentionally shows anonymous synthetic student labels only. Conflict weights count how many synthetic students take each pair of exams; the matrix is symmetric with a zero diagonal."),
    code("""registration_table=pd.DataFrame([
    {'Synthetic student':f'S-{i+1:03d}','Exams':', '.join(f'EX-{e+1:02d}' for e in row),'Exam count':len(row)}
    for i,row in enumerate(registrations[:15])])
display(registration_table)
exam_names=[f'EX-{i+1:02d}' for i in range(EXAMS)]
conflict_table=pd.DataFrame(conflict_weights,index=exam_names,columns=exam_names)
display(conflict_table)
"""),
    md("## 7. Independent guardrail audit\nThe audit is run against individual student registrations, independently of the optimizer's weighted objective."),
    code("""audit_conflicts=sum(1 for row in registrations for i,left in enumerate(row)
                     for right in row[i+1:] if best['plan'][left]==best['plan'][right])
assert len(best['plan']) == EXAMS, 'Every exam must be assigned exactly once.'
assert all(isinstance(p,int) and 0 <= p < PERIODS for p in best['plan']), 'Period out of bounds.'
assert audit_conflicts == best['clashes'], 'Independent audit must match weighted objective.'
assert len(schedule_table) == EXAMS and schedule_table['Exam'].nunique() == EXAMS
audit_table=pd.DataFrame([
    {'Check':'All exams scheduled once','Result':len(schedule_table)==EXAMS,'Observed':len(schedule_table)},
    {'Check':'All assigned periods in range','Result':all(0<=p<PERIODS for p in best['plan']),'Observed':f'0 to {PERIODS-1}'},
    {'Check':'Independent student clash audit','Result':audit_conflicts==0,'Observed':audit_conflicts},
    {'Check':'Optimizer and audit agree','Result':audit_conflicts==best['clashes'],'Observed':f'{audit_conflicts} = {best["clashes"]}'},
])
display(audit_table)
"""),
    md("## 8. Monochrome conflict visualization\nA cell is darker when more students take that exam pair. Values are synthetic and are not an institutional timetable."),
    code("""fig,ax=plt.subplots(figsize=(8,6))
image=ax.imshow(conflict_weights,cmap='Greys',interpolation='nearest')
ax.set_xticks(range(EXAMS),exam_names,rotation=45,ha='right'); ax.set_yticks(range(EXAMS),exam_names)
ax.set_title('Synthetic student conflict weights'); ax.set_xlabel('Exam'); ax.set_ylabel('Exam')
fig.colorbar(image,ax=ax,label='Shared synthetic students'); plt.tight_layout(); plt.show()
"""),
    md("## 9. Export tables\nThe CSV files are created in the Colab runtime folder. Download them from the Files panel if needed."),
    code("""benchmark_table.to_csv('benchmark_results.csv',index=False)
schedule_table.to_csv('optimized_timetable.csv',index=False)
registration_table.to_csv('synthetic_registration_sample.csv',index=False)
conflict_table.to_csv('conflict_weight_matrix.csv')
audit_table.to_csv('guardrail_audit.csv',index=False)
print('Exported: benchmark_results.csv, optimized_timetable.csv, synthetic_registration_sample.csv, conflict_weight_matrix.csv, guardrail_audit.csv')
"""),
    md("## 10. Interpretation and limits\nA zero-clash schedule means no two exams share a period for any student in this generated sample. It does not prove global optimality: PSO is stochastic and this implementation explores a constrained heuristic search space. Period capacity, rooms, invigilators, accessibility, course precedence and real-world student records are out of scope. A production timetable must add those constraints and have its data owner validate the result before use. Runtime measurements depend on the Colab hardware and session."),
]

notebook = {"cells": cells, "metadata": {"colab": {"provenance": [], "name": "NIA_Exam_Timetable_PSO.ipynb"},
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.10.12"}}, "nbformat": 4, "nbformat_minor": 5}
out = root / "notebooks" / "NIA_Exam_Timetable_PSO.ipynb"
out.write_text(json.dumps(notebook, indent=1, ensure_ascii=False), encoding="utf-8")
print(out)
