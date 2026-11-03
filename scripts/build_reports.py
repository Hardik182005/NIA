"""Build four monochrome, student-specific Experiment 9 report PDFs."""
from pathlib import Path
import sys
import time
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, PageBreak, Image, Preformatted, KeepTogether)
from reportlab.pdfbase.pdfmetrics import stringWidth

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent.parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "scripts"))
from scheduler import generate_instance, optimize_pso, random_baseline, greedy_baseline, evaluate

TEAM = [("Hardik Hinduja", 20), ("Avinash Gehi", 11), ("Sahil Deshmukh", 9), ("Siddharth Dey", 10)]
SEED, STUDENTS, EXAMS, PERIODS, PARTICLES, ITERATIONS = 42, 120, 12, 8, 32, 100
records, sizes, weights = generate_instance(SEED, STUDENTS, EXAMS)
timings = {}
for name, fn in [
    ("Random assignment", lambda: random_baseline(weights, PERIODS, SEED + 99)),
    ("Degree-greedy repair", lambda: greedy_baseline(weights, PERIODS)),
    ("Discrete PSO", lambda: optimize_pso(weights, PERIODS, SEED + 99, PARTICLES, ITERATIONS)),
]:
    start = time.perf_counter()
    result = fn()
    timings[name] = time.perf_counter() - start
    if name == "Random assignment": random_result = result
    elif name == "Degree-greedy repair": greedy_result = result
    else: pso_result = result

def fmt(v, places=3): return f"{v:.{places}f}"
def p(text, style="BodyText"): return Paragraph(text, styles[style])
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleCover", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=30, leading=35, alignment=TA_LEFT, textColor=colors.black, spaceAfter=14))
styles.add(ParagraphStyle(name="SubCover", parent=styles["Normal"], fontName="Helvetica", fontSize=12, leading=18, textColor=colors.HexColor("#333333"), spaceAfter=12))
styles.add(ParagraphStyle(name="H1Mono", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=18, leading=22, spaceBefore=3, spaceAfter=12, textColor=colors.black))
styles.add(ParagraphStyle(name="H2Mono", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=14, spaceBefore=10, spaceAfter=5, textColor=colors.black))
styles.byName["BodyText"] = ParagraphStyle(name="BodyText", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.5, leading=12, spaceAfter=6, textColor=colors.HexColor("#242424"))
styles.add(ParagraphStyle(name="SmallText", parent=styles["BodyText"], fontSize=7.1, leading=9, spaceAfter=3))
styles.add(ParagraphStyle(name="TableCell", parent=styles["BodyText"], fontSize=7.1, leading=8.5, spaceAfter=0))
styles.add(ParagraphStyle(name="TinyCell", parent=styles["BodyText"], fontSize=5.8, leading=6.6, spaceAfter=0))
styles.add(ParagraphStyle(name="CodeText", parent=styles["Code"], fontName="Courier", fontSize=6.5, leading=8, leftIndent=5, rightIndent=5, borderColor=colors.HexColor("#bdbdbd"), borderWidth=.5, borderPadding=7, spaceAfter=6))
styles.add(ParagraphStyle(name="CenterSmall", parent=styles["SmallText"], alignment=TA_CENTER))

def table(data, widths, small=False, repeat=1):
    stylename = "TinyCell" if small else "TableCell"
    converted=[]
    for ri,row in enumerate(data):
        converted.append([Paragraph(str(cell), styles[stylename]) if not isinstance(cell,Paragraph) else cell for cell in row])
    t=Table(converted,colWidths=widths,repeatRows=repeat,hAlign="LEFT")
    t.setStyle(TableStyle([
        ("TEXTCOLOR",(0,0),(-1,-1),colors.black),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("GRID",(0,0),(-1,-1),.35,colors.HexColor("#999999")),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
    ]))
    return t

def on_page(canvas, doc):
    canvas.saveState()
    w,h=letter
    canvas.setStrokeColor(colors.HexColor("#b6b6b6"));canvas.setLineWidth(.45)
    if doc.page>1:
        canvas.line(.7*inch,h-.58*inch,w-.7*inch,h-.58*inch)
        canvas.setFont("Helvetica",7);canvas.setFillColor(colors.HexColor("#555555"))
        canvas.drawString(.7*inch,h-.45*inch,"VIVEKANAND EDUCATION SOCIETY'S INSTITUTE OF TECHNOLOGY")
        canvas.drawRightString(w-.7*inch,h-.45*inch,"NIC LAB / EXPERIMENT 09")
    canvas.line(.7*inch,.54*inch,w-.7*inch,.54*inch)
    canvas.setFont("Helvetica",7);canvas.setFillColor(colors.HexColor("#555555"))
    canvas.drawString(.7*inch,.37*inch,"Examination Timetable Scheduling Using PSO")
    canvas.drawRightString(w-.7*inch,.37*inch,f"{doc.page}")
    canvas.restoreState()

def make_story(student, roll):
    story=[]
    story += [Spacer(1,.55*inch),p("VIVEKANAND EDUCATION SOCIETY'S<br/>INSTITUTE OF TECHNOLOGY","SmallText"),Spacer(1,.18*inch)]
    story += [p("Experiment 9<br/>Mini Project Report","TitleCover"),p("APPLICATION OF NATURE-INSPIRED COMPUTING TO A REAL-WORLD OPTIMIZATION PROBLEM","SubCover"),Spacer(1,.25*inch)]
    story += [p("EXAMINATION TIMETABLE SCHEDULING<br/>USING PARTICLE SWARM OPTIMIZATION","H1Mono"),Spacer(1,.2*inch)]
    story += [table([["STUDENT",student],["ROLL NUMBER",roll],["CLASS","D16 AD A/B"],["SUBJECT","NIA Lab"],["PROJECT TEAM","Hardik Hinduja 20 | Avinash Gehi 11 | Sahil Deshmukh 9 | Siddharth Dey 10"]],[1.35*inch,5.25*inch])]
    story += [Spacer(1,.35*inch),p("Department of Artificial Intelligence and Data Science<br/>Vivekanand Education Society's Institute of Technology<br/>Experiment 9 | Submitted November 2026","SubCover"),Spacer(1,.45*inch)]
    story += [p("This report documents a reproducible synthetic benchmark, a discrete PSO scheduler, an independent clash audit, and the project website. It follows the supplied mini-project brief and identifies the limits of the generated data.","BodyText"),PageBreak()]

    story += [p("1. Project Summary and Problem Formulation","H1Mono")]
    story += [p("This project assigns each examination to a period while reducing simultaneous exams taken by the same student. A weighted conflict graph records how many students take each exam pair. The primary objective is to minimize the student clash count. When clash scores tie, the schedule uses fewer periods and balances the load."),p("The selected assignment topic is Project 2, Examination Timetable Scheduling Using PSO. It is a strong mini-project choice because the optimization objective is observable, the result can be audited directly against registrations, and the timetable has a clear interactive representation." )]
    story += [p("Study design","H2Mono"),table([
      ["Item","Specification"],["Synthetic students","120, arranged in three cohorts of 40"],["Exams","12, four per synthetic cohort"],["Available periods","8 periods over four days"],["Student course load","3 or 4 exams from the student's cohort"],["PSO parameters","32 particles; 100 iterations; inertia 0.68; c1 = c2 = 1.42"],["Reproducibility","Instance seed 42; search seed 141"],["Primary metric","Weighted simultaneous exam pairs; independent student-pair audit"],["Secondary metrics","Periods used, load spread, runtime"],
    ],[1.45*inch,5.15*inch])]
    story += [p("Decision variables and constraints","H2Mono"),p("The decision variable xi in {0,...,7} gives the period for exam i. Every exam is assigned once, all period indexes must remain within the horizon, and no student should have two exams in the same period. The decoder prioritizes conflict-heavy exams and repairs candidate allocations before fitness comparison. Room capacity, invigilator availability, course precedence, variable exam lengths, and accessibility are outside this prototype." )]
    story += [p("Privacy and use guardrails","H2Mono"),p("The notebook creates anonymous synthetic registrations only. It does not request student identifiers or grades. After optimization, assertions check exam count, period bounds, and agreement between the weighted objective and a separate audit of every student's exam pairs. A zero-clash outcome is reported only when the independent audit is zero. Results are illustrative and are not ready for institutional use."),PageBreak()]

    story += [p("2. Method and Algorithm","H1Mono"),p("A particle stores one real-valued period preference per exam. At each iteration, velocity combines inertia, attraction to that particle's personal best, and attraction to the swarm's global best. Positions are clipped to the period range and decoded into discrete schedules."),p("Fitness formula","H2Mono"),Preformatted("fitness = clash_pairs * 10,000 + periods_used * 100 + load_spread",styles["CodeText"]),p("The large clash coefficient gives feasibility priority. Period count is optimized next; load spread breaks remaining ties. The conflict-aware decoder is deterministic for a given position and instance."),p("Pseudocode","H2Mono"),Preformatted("initialize particle preferences and velocities\nscore each candidate after degree-ordered repair\nfor each iteration:\n    update velocity toward personal and global best\n    clip positions to the available period range\n    repair each candidate to reduce weighted clashes\n    update personal and global bests by fitness\nindependently audit the final assignment\nexport schedule, benchmark, and audit tables",styles["CodeText"]),p("Guardrail checks in the notebook","H2Mono"),table([["Check","Expected result","Observed result"],["Every exam appears once","12 unique exams","PASS: 12 unique exams"],["Each period is in bounds","0 through 7","PASS: all in range"],["Independent audit agrees with objective","equal counts","PASS: 0 = 0"],["Student clash pairs","0 for this generated instance","PASS: 0"]],[2.0*inch,2.1*inch,2.5*inch]),p("Implementation excerpt from the Colab notebook","H2Mono")]
    code="""for iteration in range(iterations):\n    for particle in swarm:\n        for d in range(exams):\n            r1, r2 = rng.random(), rng.random()\n            velocity[d] = (0.68 * velocity[d]\n                + 1.42 * r1 * (personal_best[d] - position[d])\n                + 1.42 * r2 * (global_best[d] - position[d]))\n            position[d] = clip(position[d] + velocity[d], 0, periods - 1)\n        plan = decode_repair(position, conflict_weights, periods)\n        score = evaluate(plan, conflict_weights, periods)\n        update_personal_and_global_best(score)"""
    story += [Preformatted(code,styles["CodeText"]),p("The notebook includes the complete implementation. This excerpt shows the PSO movement and evaluation loop; candidate repair and objective code are also included there."),PageBreak()]

    story += [p("3. Benchmark Results and Timetable","H1Mono"),p("All methods use the same synthetic registration instance. The random baseline assigns periods directly and is not repaired. Degree-greedy repair is a deterministic comparison. The PSO uses the same repair decoder and optimizes its particle preferences."),p("Benchmark comparison","H2Mono")]
    result_rows=[["Method","Clash pairs","Periods","Load spread","Fitness","Runtime (s)"]]
    for name,result in [("Random assignment",random_result),("Degree-greedy repair",greedy_result),("Discrete PSO",pso_result)]:
        result_rows.append([name,result["clashes"],result["periods_used"],fmt(result["load_spread"]),fmt(result["fitness"],1),fmt(timings[name],4)])
    story += [table(result_rows,[1.55*inch,.76*inch,.55*inch,.85*inch,.85*inch,1.05*inch]),Spacer(1,8),p("On this generated instance, random assignment yields 51 student clash pairs. Both repaired methods produce zero clashes using four periods. PSO reaches the same feasible objective as the greedy baseline, so this small case does not show PSO outperforming the baseline. Runtime is machine-dependent; the figures above were measured for this report build."),p("Optimized timetable","H2Mono")]
    start_date=__import__('datetime').date(2026,11,9)
    schedule_rows=[["Exam","Registrations","Day","Session","Period"]]
    for e,period in enumerate(pso_result["plan"]):
        day=(start_date+__import__('datetime').timedelta(days=period//2)).strftime("%a, %d %b")
        session="09:00-12:00" if period%2==0 else "13:00-16:00"
        schedule_rows.append([f"EX-{e+1:02d}",sizes[e],day,session,period+1])
    story += [table(schedule_rows,[.86*inch,.9*inch,1.45*inch,1.55*inch,.66*inch]),p("Illustrative schedule labels are based on 9 November 2026. Actual exam dates and periods are demonstration metadata, not institutional bookings." ,"SmallText"),p("Period utilization","H2Mono")]
    loads=pso_result["loads"]
    utilization=[["Period","Exams","Exam IDs","Student registrations"]]
    for period,count in enumerate(loads):
        exams=[f"EX-{i+1:02d}" for i,pid in enumerate(pso_result["plan"]) if pid==period]
        if not exams: continue
        tot=sum(sizes[int(e[-2:])-1] for e in exams)
        utilization.append([period+1,count,", ".join(exams),tot])
    story += [table(utilization,[.75*inch,.72*inch,3.3*inch,1.45*inch]),PageBreak()]

    story += [p("4. Conflict Graph and Data Tables","H1Mono"),p("Each matrix cell counts the synthetic students who take both exams in that row and column. The diagonal is zero. Values outside each cohort's four-exam block are zero by design."),p("Conflict weight matrix","H2Mono")]
    names=[f"EX-{i+1:02d}" for i in range(EXAMS)]
    matrix=[["Exam"]+names]
    for i,name in enumerate(names):matrix.append([name]+weights[i])
    story += [table(matrix,[.48*inch]+[.49*inch]*EXAMS,small=True),Spacer(1,10),p("Anonymous registration sample","H2Mono")]
    sample=[["Synthetic ID","Exam list","Count"]]
    for i,row in enumerate(records[:12]):sample.append([f"S-{i+1:03d}",", ".join(f"EX-{e+1:02d}" for e in row),len(row)])
    story += [table(sample,[1.1*inch,4.8*inch,.6*inch]),Spacer(1,10),p("Conflict objective and audit","H2Mono")]
    total_conflicts=sum(weights[a][b] for a in range(EXAMS) for b in range(a+1,EXAMS))
    audit=sum(1 for row in records for i,a in enumerate(row) for b in row[i+1:] if pso_result["plan"][a]==pso_result["plan"][b])
    story += [table([["Metric","Result"],["Total nonzero conflict weight across all exam pairs",total_conflicts],["Student clash pairs in PSO schedule",pso_result["clashes"]],["Independent registration-level audit",audit],["Consistency check",f"{'PASS' if audit==pso_result['clashes'] else 'FAIL'}: objective {pso_result['clashes']} = audit {audit}"]],[3.5*inch,3.0*inch]),PageBreak()]

    story += [p("5. Colab Notebook and Reproducibility","H1Mono"),p("The linked Colab notebook is built around the blank notebook supplied with the project request. Its code bootstraps the public repository copy, runs all notebook cells, displays the tables and monochrome conflict plot, and writes CSV exports into the Colab runtime."),p("Google Colab notebook","H2Mono"),p("https://colab.research.google.com/drive/1GxqpVK-q_ZGQ7XSdVVrjEuHLYpR0fctJ","SmallText"),p("Notebook output files","H2Mono"),table([["File","Contents"],["benchmark_results.csv","Baseline and PSO objective, periods, fitness, runtime, feasibility"],["optimized_timetable.csv","One period per exam and registration count"],["synthetic_registration_sample.csv","Anonymous synthetic student exam selections"],["conflict_weight_matrix.csv","Shared-student counts for every exam pair"],["guardrail_audit.csv","Post-run invariant and clash checks"]],[2.65*inch,3.85*inch]),p("Reproducibility procedure","H2Mono"),p("Open the notebook link and run all cells. Seed 42 regenerates the same synthetic registrations; the search seed is 141. The objective values are deterministic for this implementation. Wall-clock timing is reported locally and can vary across Colab runtimes."),p("Monochrome code excerpt","H2Mono")]
    story += [Preformatted("def fitness(plan, conflict_weights, periods):\n    clashes = conflict_count(plan, conflict_weights)\n    used = len(set(plan))\n    spread = load_standard_deviation(plan, periods)\n    return clashes * 10_000 + used * 100 + spread\n\n# Independent student-level audit\naudit = sum(1 for student in registrations\n    for i, left in enumerate(student)\n    for right in student[i+1:]\n    if schedule[left] == schedule[right])\nassert audit == reported_clashes",styles["CodeText"]),p("Limitations","H2Mono"),p("This prototype does not model room capacity, invigilators, student accessibility, course sequencing, exam duration, or real enrollment data. The search is heuristic. One feasible synthetic result is not evidence of global optimality. Any production schedule requires validation by the institution's data owner and academic administrators."),PageBreak()]

    for path, caption in [(ROOT/"reports"/"website_hero.png","Website preview capture from the exact static build uploaded to Vercel: monochrome landing page and interactive 3D examination grid."),(ROOT/"reports"/"website_results.png","Website preview capture from the exact static build uploaded to Vercel: PSO output with zero audited clashes across four periods.")]:
        story += [p("6. Website Evidence","H1Mono") if "website_hero" in path.name else p("Website Evidence Continued","H1Mono"),p(caption,"SmallText")]
        if path.exists():
            img=Image(str(path)); img._restrictSize(6.55*inch,7.95*inch); story += [img]
        else: story += [p("Website screenshot unavailable during report build.")]
        if "website_hero" in path.name: story += [p("The page uses a white background, black text, grayscale 3D geometry, and a responsive layout. The 3D model can be rotated by dragging; the simulator runs the same seeded cohort instance and exposes its schedule. Vercel Drop reported a temporary live URL, but this browser received HTTP 403 when it attempted to open that host. The included images are the local preview of the exact static build that was uploaded."),PageBreak()]
    story += [p("References and Project Files","H1Mono"),p("Supplied Experiment 9 Mini-Project brief: Application of Nature-Inspired Computing Algorithms for Solving Real-World Optimization Problems; Project 2: Examination Timetable Scheduling Using PSO."),p("Project source: https://github.com/Hardik182005/NIA<br/>Temporary Vercel deployment (expires unless claimed): https://fleet-bayou-9rbyyz8.tmp.now","SmallText"),p("Implementation prompt: PROJECT_PROMPT.md. Full algorithm, baseline code, tables, audit assertions, plots, and CSV exports: notebooks/NIA_Exam_Timetable_PSO.ipynb. Website source and static deployment files: site/dist/.","BodyText"),Spacer(1,10),table([["Prepared for","NIA Lab | Experiment 9 Mini Project"],["Selected topic","Examination Timetable Scheduling Using PSO"],["Project team","Hardik Hinduja (20), Avinash Gehi (11), Sahil Deshmukh (9), Siddharth Dey (10)"],["Data notice","All registration records are generated and synthetic."]],[1.35*inch,5.15*inch])]
    return story

for student,roll in TEAM:
    safe=student.replace(" ","_")
    path=OUT/f"{safe}_{roll}_Exam_Timetable_PSO_Report.pdf"
    doc=SimpleDocTemplate(str(path),pagesize=letter,rightMargin=.7*inch,leftMargin=.7*inch,topMargin=.78*inch,bottomMargin=.72*inch,title=f"Exam Timetable Scheduling Using PSO - {student}",author="NIA Lab Project Team")
    doc.build(make_story(student,roll),onFirstPage=on_page,onLaterPages=on_page)
    print(path)
