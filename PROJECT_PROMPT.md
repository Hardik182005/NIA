# Implementation Prompt

Build a complete, reproducible Experiment 9 Nature-Inspired Computing mini project for **Project 5: Vehicle Route Optimization Using Ant Colony Optimization (ACO)**.

Create a small, deterministic, fully synthetic ten-location coordinate set: one depot and nine delivery stops. Build an Euclidean distance matrix and optimize a closed tour that visits every stop exactly once before returning to the depot. Implement ACO with roulette-wheel transition probabilities, pheromone evaporation/deposition, a fixed random seed, and a 2-opt improvement pass. Compare a mean of seeded random tours, nearest-neighbor, ACO, and exact enumeration of all 9! tours. Report runtime as environment-dependent, and never describe synthetic coordinates as a real map or road distance.

Add an independent route audit that checks depot start/end, stop uniqueness/completeness, and independently recomputes the distance by summing the route legs. Generate plain monochrome tables for parameters, synthetic locations, comparison metrics, route order and legs, full distance matrix, convergence, and audit. Export CSVs.

Build a responsive minimal white-background, black-text website with a working draggable Three.js 3D route visualization, a Run ACO interaction, and a route-leg table. Use grayscale geometry and readable mobile layouts.

Include explicit privacy and operational guardrails: never use private addresses or customer data; explain that Euclidean coordinate distance is not road routing; disclose missing traffic, capacity, time-window, and driver constraints; and state that the project is educational rather than dispatch-ready. Create four individual report PDFs with plain black-and-white tables and separate covers for Hardik Hinduja (20), Avinash Gehi (11), Sahil Deshmukh (9), and Siddharth Dey (10). Do not claim superiority beyond the evidence from this one small synthetic instance.
