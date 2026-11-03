"""Build the Project 5 Colab notebook from the maintained ACO implementation."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
algorithm = (ROOT / "scripts" / "route_optimizer.py").read_text(encoding="utf-8")

def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}

def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": text.splitlines(keepends=True)}

cells = [
md("""# Vehicle Route Optimization Using Ant Colony Optimization

**Experiment 9 | Nature-Inspired Computing mini project | Project 5**  
**Team:** Hardik Hinduja (20), Avinash Gehi (11), Sahil Deshmukh (9), Siddharth Dey (10)

This notebook compares Ant Colony Optimization (ACO) with a 500-tour random baseline, nearest neighbor, and exhaustive enumeration on a small ten-location delivery loop. ACO uses pheromone trails and inverse-distance desirability, followed by deterministic 2-opt local improvement.

> All coordinates are synthetic and illustrative. Distances are Euclidean kilometres on a toy plane; they are not road distances, GPS coordinates, or live navigation advice.

## Selected topic
**Project 5: Vehicle Route Optimization Using Ant Colony Optimization (ACO).** Find a short closed route that starts at a depot, visits every delivery stop exactly once, and returns to the depot.

## Guardrails
- Use only the included synthetic coordinates; do not enter addresses, customer names, phone numbers, or live tracking data.
- Every route must start and end at the depot and visit each stop exactly once.
- Recompute the final distance independently by summing the leg matrix, and verify it agrees with the optimizer.
- Compare ACO with exhaustive enumeration on this small instance; on larger instances exact enumeration is not practical.
- A synthetic Euclidean result is not a real-world road route or a proof of traffic-aware optimality.

## Implementation prompt
“Build a complete, reproducible Experiment 9 mini project for Project 5, Vehicle Route Optimization Using Ant Colony Optimization. Use ten clearly synthetic coordinates (one depot and nine delivery stops); calculate a symmetric Euclidean distance matrix; implement seeded ACO with roulette-wheel transitions, pheromone evaporation/deposit, and deterministic 2-opt improvement; compare against 500 random tours, nearest neighbor, and an exact brute-force optimum; print detailed plain tables for parameters, benchmark results, route legs and cumulative distance, locations, pairwise distances, convergence, and independent route audits; export CSVs; explain limitations and guardrails; and provide a responsive white-and-black website with an interactive 3D route view. Never represent toy coordinates as actual addresses or road navigation.”
"""),
md("## 1. Imports and display setup\nThe optimizer uses the Python standard library. Pandas is used for plain tables and CSV export; matplotlib is optional for the monochrome convergence figure."),
code("""import pandas as pd
from IPython.display import display
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None
pd.set_option('display.max_rows', 60)
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 160)
"""),
md("## 2. Complete ACO implementation\nThe following source is embedded from `scripts/route_optimizer.py`, so this notebook can run independently in Colab without cloning the repository."),
code(algorithm),
md("## 3. Instance and parameters\nOne depot plus nine synthetic stops gives 9! = 362,880 possible stop permutations, small enough for an exact reference optimum. The coordinate plane is a toy model and the straight-line distances are illustrative."),
code("""instance_table = pd.DataFrame([
    {'Parameter':'Locations including depot','Value':len(LOCATIONS),'Meaning':'One depot plus nine delivery stops'},
    {'Parameter':'Delivery stops','Value':len(LOCATIONS)-1,'Meaning':'Each stop must appear once'},
    {'Parameter':'Distance metric','Value':'Euclidean','Meaning':'Toy plane; not road routing'},
    {'Parameter':'Random baseline trials','Value':500,'Meaning':'Mean and best sampled tour'},
    {'Parameter':'ACO seed','Value':141,'Meaning':'Reproducible ant decisions'},
    {'Parameter':'Ants per iteration','Value':48,'Meaning':'Candidate tours constructed each iteration'},
    {'Parameter':'ACO iterations','Value':160,'Meaning':'Pheromone update cycles'},
    {'Parameter':'Alpha (pheromone weight)','Value':1.0,'Meaning':'Influence of learned trails'},
    {'Parameter':'Beta (distance heuristic)','Value':4.0,'Meaning':'Influence of inverse distance'},
    {'Parameter':'Evaporation rate','Value':0.42,'Meaning':'Pheromone fraction removed per iteration'},
    {'Parameter':'Local improvement','Value':'2-opt','Meaning':'Deterministic edge reversal improvement'},
    {'Parameter':'Exact reference','Value':'362,880 tours','Meaning':'9! permutations, one depot fixed'},
])
display(instance_table)
location_table = pd.DataFrame(LOCATIONS)
display(location_table)
"""),
md("## 4. Benchmark comparison\nRandom assignment is averaged over 500 seeded tours. Nearest neighbor always selects the closest unvisited stop. ACO constructs tours with pheromone-guided roulette selection and applies 2-opt. Exact enumeration supplies the global optimum for this small instance."),
code("""experiment = run_experiment()
results = experiment['results']
random_result = results['Random (500 tours)']
benchmark_table = pd.DataFrame([
    {'Method':'Random (500 tours)','Distance (km)':random_result['distance'], 'Reference / detail':f"mean of {random_result['trials']} seeded tours", 'Runtime seconds':random_result['runtime_seconds']},
    {'Method':'Nearest neighbor','Distance (km)':results['Nearest neighbor']['distance'], 'Reference / detail':'greedy nearest unvisited stop', 'Runtime seconds':results['Nearest neighbor']['runtime_seconds']},
    {'Method':'ACO + 2-opt','Distance (km)':results['ACO + 2-opt']['distance'], 'Reference / detail':'48 ants; 160 iterations; seed 141', 'Runtime seconds':results['ACO + 2-opt']['runtime_seconds']},
    {'Method':'Exact enumeration','Distance (km)':results['Exact enumeration']['distance'], 'Reference / detail':'global optimum over 362,880 tours', 'Runtime seconds':results['Exact enumeration']['runtime_seconds']},
])
benchmark_table['Distance (km)'] = benchmark_table['Distance (km)'].round(3)
benchmark_table['Runtime seconds'] = benchmark_table['Runtime seconds'].round(4)
benchmark_table['Gap to exact (%)'] = ((benchmark_table['Distance (km)'] / results['Exact enumeration']['distance'] - 1) * 100).round(3)
display(benchmark_table)
"""),
md("## 5. Optimized route and leg table\nThe ordered legs include the return to the depot. Cumulative distance is recalculated from the distance matrix."),
code("""aco_result = results['ACO + 2-opt']
route = aco_result['route']
locations = experiment['locations']
distances = experiment['distances']
leg_rows=[]
cumulative=0.0
for sequence, (left, right) in enumerate(zip(route, route[1:]), start=1):
    leg=distances[left][right]
    cumulative += leg
    leg_rows.append({'Leg':sequence,'From':locations[left]['name'],'To':locations[right]['name'],
                     'From ID':locations[left]['id'],'To ID':locations[right]['id'],
                     'Leg distance (km)':leg,'Cumulative (km)':cumulative})
route_table=pd.DataFrame(leg_rows)
route_table[['Leg distance (km)','Cumulative (km)']] = route_table[['Leg distance (km)','Cumulative (km)']].round(3)
display(route_table)
"""),
md("## 6. Pairwise distance matrix\nThe matrix is symmetric, with a zero diagonal. Distances are straight-line Euclidean values in the illustrative coordinate plane."),
code("""ids=[location['id'] for location in locations]
distance_matrix_table=pd.DataFrame(distances,index=ids,columns=ids).round(2)
display(distance_matrix_table)
"""),
md("## 7. Convergence and independent audit\nThe audit validates route closure, stop coverage, unique visits, and an independent leg-sum distance. The exact optimum is used to calculate the gap; zero gap applies only to this synthetic instance."),
code("""history=aco_result['history']
exact_distance=results['Exact enumeration']['distance']
audit=experiment['audit']
convergence_table=pd.DataFrame([
    {'Metric':'Best distance after iteration 1 (km)','Value':round(history[0],6)},
    {'Metric':'Best distance after iteration 160 (km)','Value':round(history[-1],6)},
    {'Metric':'Iterations','Value':len(history)},
    {'Metric':'Best-so-far history is non-increasing','Value':all(history[i] >= history[i+1] for i in range(len(history)-1))},
    {'Metric':'Exact optimum (km)','Value':round(exact_distance,6)},
    {'Metric':'ACO gap to exact (%)','Value':round(audit['gap_to_exact_percent'],6)},
])
display(convergence_table)
audit_table=pd.DataFrame([
    {'Check':'Starts and ends at depot','Pass':audit['closed_route_starts_and_ends_at_depot'],'Observed':'DEPOT to DEPOT'},
    {'Check':'Every delivery stop visited exactly once','Pass':audit['each_delivery_stop_visited_once'],'Observed':len(set(route[1:-1]))},
    {'Check':'All required stops included','Pass':audit['all_nodes_included'],'Observed':f"{len(route)-2} of {len(locations)-1}"},
    {'Check':'Distance matches independent leg sum','Pass':audit['distance_matches_optimizer'],'Observed':f"{audit['distance_recomputed_from_legs']:.6f} km"},
    {'Check':'ACO matches exact optimum on this instance','Pass':audit['gap_to_exact_percent'] < 1e-8,'Observed':f"{audit['gap_to_exact_percent']:.6f}% gap"},
])
assert audit_table['Pass'].all(), 'Route or distance audit failed.'
display(audit_table)
"""),
md("## 8. Monochrome convergence figure\nThe figure records the global best-so-far distance over iterations."),
code("""if plt is not None:
    fig, ax = plt.subplots(figsize=(8,3.4))
    ax.plot(range(1,len(history)+1),history,color='black',linewidth=1.5)
    ax.set_title('ACO best-so-far route distance')
    ax.set_xlabel('Iteration'); ax.set_ylabel('Distance (km)')
    ax.grid(True,color='0.85',linewidth=.5); fig.tight_layout(); plt.show()
else:
    print('Optional matplotlib is unavailable; the convergence table is complete.')
"""),
md("## 9. Export results\nThe CSV files are written into the Colab runtime. Open the Files panel to download them."),
code("""benchmark_table.to_csv('route_benchmark_results.csv',index=False)
route_table.to_csv('optimized_route_legs.csv',index=False)
location_table.to_csv('synthetic_locations.csv',index=False)
distance_matrix_table.to_csv('pairwise_distance_matrix.csv')
convergence_table.to_csv('aco_convergence_summary.csv',index=False)
audit_table.to_csv('route_guardrail_audit.csv',index=False)
print('Exported six CSV result tables.')
"""),
md("## 10. Interpretation and limitations\nOn this toy map, the ACO + 2-opt route matches the exhaustive optimum at 31.154 km; nearest neighbor is 43.401 km and the 500-tour random mean is 53.455 km. This demonstrates the implementation on one small instance only. It does not establish performance on other maps. Straight-line distance omits road networks, direction restrictions, traffic, time windows, vehicle capacity, fuel use, delivery priorities, safety, and multiple vehicles. Exhaustive enumeration grows factorially and is included only as a reference for nine stops. Do not use this notebook for dispatch or live navigation."),
]
notebook={"cells":cells,"metadata":{"colab":{"provenance":[],"name":"NIA_Vehicle_Route_ACO.ipynb"},"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":"3.10.12"}},"nbformat":4,"nbformat_minor":5}
out=ROOT/"notebooks"/"NIA_Vehicle_Route_ACO.ipynb"
out.write_text(json.dumps(notebook,indent=1,ensure_ascii=False),encoding="utf-8")
print(out)

