"""Build four individualized monochrome Experiment 9 ACO project reports."""
from pathlib import Path
import sys
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, Preformatted, KeepTogether

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(r"C:\Users\hardi\Documents\Codex\2026-11-03\take\outputs")
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "scripts"))
from route_optimizer import run_experiment, route_distance

DATA = run_experiment()
LOC = DATA["locations"]
DIST = DATA["distances"]
RESULTS = DATA["results"]
ACO = RESULTS["ACO + 2-opt"]
AUDIT = DATA["audit"]
TEAM = [("Hardik Hinduja", 20), ("Avinash Gehi", 11), ("Sahil Deshmukh", 9), ("Siddharth Dey", 10)]

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=27, leading=32, alignment=TA_LEFT, textColor=colors.black, spaceAfter=12))
styles.add(ParagraphStyle(name="CoverSub", parent=styles["Normal"], fontName="Helvetica", fontSize=10, leading=15, textColor=colors.black, spaceAfter=9))
styles.add(ParagraphStyle(name="Section", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=17, leading=20, spaceBefore=2, spaceAfter=9, textColor=colors.black))
styles.add(ParagraphStyle(name="Subsection", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=10.5, leading=13, spaceBefore=8, spaceAfter=4, textColor=colors.black))
styles.add(ParagraphStyle(name="BodyMono", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.1, leading=10.5, spaceAfter=5, textColor=colors.black))
styles.add(ParagraphStyle(name="SmallMono", parent=styles["BodyText"], fontName="Helvetica", fontSize=6.8, leading=8, spaceAfter=3, textColor=colors.black))
styles.add(ParagraphStyle(name="CellMono", parent=styles["BodyText"], fontName="Helvetica", fontSize=6.3, leading=7.4, spaceAfter=0, textColor=colors.black))
styles.add(ParagraphStyle(name="TinyMono", parent=styles["BodyText"], fontName="Helvetica", fontSize=4.7, leading=5.5, spaceAfter=0, textColor=colors.black))
styles.add(ParagraphStyle(name="CodeMono", parent=styles["Code"], fontName="Courier", fontSize=6.2, leading=7.5, leftIndent=4, rightIndent=4, borderColor=colors.black, borderWidth=.4, borderPadding=5, spaceAfter=5))


def para(text, style="BodyMono"):
    return Paragraph(str(text), styles[style])


def grid(rows, widths, tiny=False, repeat=1):
    sty = styles["TinyMono"] if tiny else styles["CellMono"]
    data = [[cell if isinstance(cell, Paragraph) else Paragraph(str(cell), sty) for cell in row] for row in rows]
    tbl = Table(data, colWidths=widths, repeatRows=repeat, hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), .35, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return tbl


def page_decor(canvas, doc):
    canvas.saveState()
    w, h = letter
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(.4)
    if doc.page > 1:
        canvas.line(.68*inch, h-.56*inch, w-.68*inch, h-.56*inch)
        canvas.setFont("Helvetica", 6.5)
        canvas.drawString(.68*inch, h-.43*inch, "VIVEKANAND EDUCATION SOCIETY'S INSTITUTE OF TECHNOLOGY")
        canvas.drawRightString(w-.68*inch, h-.43*inch, "NIC LAB / EXPERIMENT 09")
    canvas.line(.68*inch, .52*inch, w-.68*inch, .52*inch)
    canvas.setFont("Helvetica", 6.5)
    canvas.drawString(.68*inch, .35*inch, "Vehicle Route Optimization Using ACO")
    canvas.drawRightString(w-.68*inch, .35*inch, str(doc.page))
    canvas.restoreState()


def route_stop_rows():
    route = ACO["route"]
    rows = [["Leg", "From", "To", "Distance (km)", "Cumulative (km)"]]
    cumulative = 0.0
    for step, (left, right) in enumerate(zip(route, route[1:]), 1):
        length = DIST[left][right]
        cumulative += length
        rows.append([step, LOC[left]["name"], LOC[right]["name"], f"{length:.3f}", f"{cumulative:.3f}"])
    return rows


def story_for(student, roll):
    story = [Spacer(1, .55*inch), para("VIVEKANAND EDUCATION SOCIETY'S<br/>INSTITUTE OF TECHNOLOGY", "SmallMono"), Spacer(1, .17*inch),
             para("Experiment 9<br/>Mini Project Report", "CoverTitle"),
             para("APPLICATION OF NATURE-INSPIRED COMPUTING TO A REAL-WORLD OPTIMIZATION PROBLEM", "CoverSub"), Spacer(1, .22*inch),
             para("VEHICLE ROUTE OPTIMIZATION<br/>USING ANT COLONY OPTIMIZATION", "Section"), Spacer(1, .17*inch),
             grid([["STUDENT", student], ["ROLL NUMBER", roll], ["CLASS", "D16 AD A/B"], ["SUBJECT", "NIA Lab"],
                   ["PROJECT TEAM", "Hardik Hinduja 20 | Avinash Gehi 11 | Sahil Deshmukh 9 | Siddharth Dey 10"]], [1.35*inch, 5.1*inch]),
             Spacer(1, .3*inch), para("Department of Artificial Intelligence and Data Science<br/>Vivekanand Education Society's Institute of Technology<br/>Experiment 9 Mini Project | November 2026", "CoverSub"), Spacer(1, .25*inch),
             para("A reproducible synthetic delivery-route study using Ant Colony Optimization, a nearest-neighbor baseline, a random-tour baseline, exact enumeration, and an independent route audit. All locations and distances in this demonstration are synthetic.") , PageBreak()]

    story += [para("1. Project Summary and Problem Formulation", "Section"),
              para("Selected topic: Project 5, Vehicle Route Optimization Using Ant Colony Optimization (ACO). The task finds a short closed tour that starts at a depot, visits every delivery stop once, and returns to the depot. The demonstration uses Euclidean distance on a small synthetic coordinate map."),
              para("Study design", "Subsection"),
              grid([["Item", "Specification"], ["Locations", "10 total: one depot and nine synthetic stops"], ["Distance model", "Euclidean distance in illustrative kilometre units"], ["Route structure", "Start at depot, visit each stop once, return to depot"], ["ACO ants", str(ACO["ants"])], ["ACO iterations", str(ACO["iterations"])], ["Parameters", f"alpha={ACO['alpha']}; beta={ACO['beta']}; evaporation={ACO['evaporation']}; deposit=100"], ["Seed", str(ACO["seed"])], ["Validation", "Exhaustive enumeration of 9! possible tours"], ["Primary metric", "Closed-tour distance in km"]], [1.45*inch, 5.0*inch]),
              para("Decision variables and constraints", "Subsection"),
              para("A solution is an ordered permutation of all nine delivery stops between two depot entries. Every stop must appear exactly once; the depot must be both the first and last node; all route legs use nonnegative distances from the symmetric matrix. The report recomputes total distance from each consecutive pair of stops. Real road networks, traffic, vehicle capacities, time windows, driver hours, route restrictions, and live addresses are out of scope."),
              para("Privacy and use guardrails", "Subsection"),
              para("The map is fully synthetic and uses no customer names, addresses, or personal delivery records. The application must not be populated with private addresses without authorization and suitable privacy controls. Distance is straight-line demonstration distance, not an operational travel estimate. Exact enumeration provides a lower bound and validity reference only for this ten-node instance."), PageBreak()]

    story += [para("2. ACO Method and Implementation", "Section"),
              para("Each ant builds a tour one stop at a time. The transition weight combines the pheromone trail on an edge with inverse distance. After a tour is complete, 2-opt reverses sub-paths whenever that shortens the closed tour. Pheromone evaporates, then the iteration-best and global-best tours deposit pheromone on their edges."),
              para("Transition and pheromone rules", "Subsection"),
              Preformatted("probability(i -> j) proportional to pheromone(i,j)^alpha * (1/distance(i,j))^beta\npheromone <- (1 - evaporation) * pheromone\niteration-best and global-best tours deposit Q / route_length", styles["CodeMono"]),
              para("Pseudocode", "Subsection"),
              Preformatted("initialize symmetric pheromone and inverse-distance heuristic\nfor each iteration:\n    for each ant:\n        grow a closed tour using roulette-wheel transitions\n        improve the tour with deterministic 2-opt\n    evaporate pheromone\n    reinforce iteration-best and global-best edges\nindependently verify route structure and recompute every leg", styles["CodeMono"]),
              para("Validation checks", "Subsection"),
              grid([["Check", "Expected", "Observed"], ["Depot starts and ends route", "True", str(AUDIT["closed_route_starts_and_ends_at_depot"])], ["Every delivery stop appears once", "9 unique stops", str(AUDIT["each_delivery_stop_visited_once"])], ["All stops included", "All 9 IDs", str(AUDIT["all_nodes_included"])], ["Optimizer equals recomputed legs", "Equal to 1e-9 km", str(AUDIT["distance_matches_optimizer"])], ["ACO route is valid", "True", str(AUDIT["route_is_valid"])], ["Gap to exact optimum", "Reported transparently", f"{AUDIT['gap_to_exact_percent']:.6f}%"]], [2.15*inch, 2.1*inch, 2.2*inch]),
              para("Implementation excerpt", "Subsection"),
              Preformatted("for ant in range(ants):\n    route = [depot]\n    while unvisited_stops:\n        next_stop = roulette_wheel(pheromone, inverse_distance)\n        route.append(next_stop)\n    route.append(depot)\n    route = two_opt(route, distances)\n    update_best_route(route)\n\nassert independent_audit(route).route_is_valid", styles["CodeMono"]), PageBreak()]

    story += [para("3. Benchmark Results and Best Route", "Section"),
              para("All methods use the same ten-location distance matrix. The random baseline reports the mean and best of 500 seeded tours; nearest neighbor is deterministic; ACO uses 48 ants for 160 iterations with 2-opt; exact enumeration checks every one of the 9! possible delivery-stop permutations."),
              para("Benchmark comparison", "Subsection")]
    rows = [["Method", "Distance (km)", "Runtime (s)", "Notes"]]
    for name, result in RESULTS.items():
        if name == "Random (500 tours)":
            rows.append([name, f"Mean {result['distance']:.3f}; best {result['best_distance']:.3f}", f"{result['runtime_seconds']:.4f}", "500 seeded tours"])
        else:
            note = {"Nearest neighbor": "Greedy nearest unvisited stop", "ACO + 2-opt": "ACO candidate and 2-opt refinement", "Exact enumeration": "Global optimum for this small instance"}[name]
            rows.append([name, f"{result['distance']:.3f}", f"{result['runtime_seconds']:.4f}", note])
    story += [grid(rows, [1.35*inch, 1.3*inch, .82*inch, 2.95*inch]), Spacer(1, 6),
              para(f"ACO + 2-opt returns {ACO['distance']:.3f} km. Exact enumeration also returns {RESULTS['Exact enumeration']['distance']:.3f} km, so the best route on this synthetic instance matches the enumerated optimum with a {AUDIT['gap_to_exact_percent']:.6f}% gap. This does not establish that ACO always finds an optimum; the exact check is feasible here because there are only nine delivery stops."),
              para("Optimal closed route", "Subsection")]
    route_names = " -> ".join(LOC[i]["name"] for i in ACO["route"])
    story += [para(route_names, "SmallMono"), Spacer(1, 5), grid(route_stop_rows(), [.38*inch, 1.65*inch, 1.65*inch, 1.25*inch, 1.42*inch]),
              Spacer(1, 6), grid([["Best route distance", "Stops", "Legs", "Exact gap"], [f"{ACO['distance']:.3f} km", "9", "10", f"{AUDIT['gap_to_exact_percent']:.6f}%"]], [1.65*inch, 1.45*inch, 1.5*inch, 1.75*inch]), PageBreak()]

    story += [para("4. Synthetic Map and Distance Tables", "Section"),
              para("The coordinate locations are invented solely to make the optimization reproducible. The distance matrix is symmetric with a zero diagonal. Values are Euclidean units presented as illustrative kilometres; they are not road distances."),
              para("Location coordinates", "Subsection"),
              grid([["ID", "Location", "X", "Y"]] + [[x["id"], x["name"], f"{x['x']:.1f}", f"{x['y']:.1f}"] for x in LOC], [.85*inch, 2.7*inch, 1.15*inch, 1.15*inch]),
              para("Pairwise distance matrix (km)", "Subsection")]
    labels = [x["id"].replace("STOP-", "S") for x in LOC]
    matrix = [["From / to"] + labels]
    for i, loc in enumerate(LOC):
        matrix.append([labels[i]] + [f"{DIST[i][j]:.1f}" for j in range(len(LOC))])
    story += [grid(matrix, [.63*inch] + [.58*inch]*len(LOC), tiny=True), Spacer(1, 8),
              para("The ACO total is independently computed as the sum of the ten ordered route-leg distances. The complete distance matrix is included so that each result can be reproduced or recalculated without relying on a map service."), PageBreak()]

    story += [para("5. Colab Notebook and Reproducibility", "Section"),
              para("The linked Colab notebook bootstraps the public project repository, runs the self-contained route optimization cells, prints the full benchmark and route tables, draws a black-and-white convergence chart, and exports CSV files."),
              para("Google Colab notebook", "Subsection"),
              para("https://colab.research.google.com/drive/1GxqpVK-q_ZGQ7XSdVVrjEuHLYpR0fctJ", "SmallMono"),
              para("Notebook result tables and CSV exports", "Subsection"),
              grid([["Output", "Description"], ["Benchmark comparison", "Random 500-tour mean/best, nearest neighbor, ACO + 2-opt, exact optimum and runtime"], ["Best route legs", "Every ordered stop-to-stop leg and cumulative distance"], ["Synthetic locations", "Location IDs and X/Y coordinates"], ["Distance matrix", "All 100 symmetric pairwise distances"], ["Independent audit", "Route closure, one visit per stop, complete stop set, recomputed distance and exact gap"], ["Convergence data", "Best-so-far distance for each ACO iteration"], ["CSV files", "route_benchmark_results.csv, optimized_route_legs.csv, synthetic_locations.csv, pairwise_distance_matrix.csv, aco_convergence_summary.csv, route_guardrail_audit.csv"]], [1.65*inch, 4.8*inch]),
              para("Reproduction steps", "Subsection"),
              para("Open the notebook link and run all cells. The map and algorithm seed are fixed. The random baseline samples 500 tours; exact enumeration explores every permutation of nine stops. Runtime is measured per run and varies by hardware."),
              para("Scope limits", "Subsection"),
              para("This synthetic benchmark does not model roads, traffic, travel-time variation, vehicle capacity, time windows, depot hours, loading limits, driver breaks, or legal routing restrictions. It is a class project demonstration, not dispatch advice. Do not infer operational route quality from straight-line distance."),
              Preformatted("route_distance = sum(distance[route[i]][route[i + 1]]\n                     for i in range(len(route) - 1))\nassert route[0] == route[-1] == depot\nassert sorted(route[1:-1]) == all_delivery_stops", styles["CodeMono"]), PageBreak()]

    for filename, caption, heading in [("website_hero.png", "Landing page showing the monochrome 3D route network.", "6. Website Evidence"),
                                       ("website_results.png", "Interactive ACO results table and route distance output.", "7. Website Results Evidence")]:
        story += [para(heading, "Section"), para(caption, "SmallMono")]
        img_path = ROOT / "reports" / filename
        if img_path.exists():
            img = Image(str(img_path))
            img._restrictSize(6.55*inch, 7.9*inch)
            story.append(img)
        else:
            story.append(para(f"Screenshot placeholder: {filename} will be supplied by the refreshed Project 5 website build."))
        story.append(para("The website is designed with a white background, black text, grayscale 3D location pins, and an interactive route line. Drag the scene to rotate the model; the ACO control displays a computed route. The production website is deployed at https://nia-dist.vercel.app/ and was checked successfully with an HTTP 200 response and the expected Routecraft page title. The included screenshots show the same monochrome 3D website."))
        if filename == "website_hero.png":
            story.append(PageBreak())
    story += [para("References and Project Files", "Subsection"),
              para("Supplied Experiment 9 mini-project brief: Project 5, Vehicle Route Optimization Using Ant Colony Optimization."),
              para("Project repository: https://github.com/Hardik182005/NIA<br/>Production website: https://nia-dist.vercel.app/"),
              para("Implementation prompt: PROJECT_PROMPT.md. Source implementation: scripts/route_optimizer.py. Notebook: notebooks/NIA_Vehicle_Route_ACO.ipynb. Website source: site/dist/."),
              grid([["Prepared for", "NIA Lab | Experiment 9 Mini Project"], ["Selected topic", "Project 5: Vehicle Route Optimization Using ACO"], ["Team", "Hardik Hinduja 20 | Avinash Gehi 11 | Sahil Deshmukh 9 | Siddharth Dey 10"], ["Data notice", "Synthetic coordinates and distances only"]], [1.2*inch, 5.25*inch])]
    return story


for student, roll in TEAM:
    filename = f"{student.replace(' ', '_')}_{roll}_Vehicle_Route_ACO_Report.pdf"
    path = OUT / filename
    doc = SimpleDocTemplate(str(path), pagesize=letter, rightMargin=.68*inch, leftMargin=.68*inch, topMargin=.75*inch, bottomMargin=.68*inch, title=f"Vehicle Route Optimization Using ACO - {student}", author="NIA Lab Project Team")
    doc.build(story_for(student, roll), onFirstPage=page_decor, onLaterPages=page_decor)
    print(path)
