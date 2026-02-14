# 🧠 Tactic Fingerprint Generator

> Tactical DNA Modeling from Event-Level Football Data

![Status](https://img.shields.io/badge/status-in%20development-orange)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/data-StatsBomb%20Open%20Data-lightgrey)

---

## 🎯 Overview

**Tactic Fingerprint Generator** is a football analytics system that converts raw match event data into structured tactical identities for teams.

Instead of modeling outcomes (goals, xG, wins), this project models **how teams play** — their spatial control, passing tendencies, verticality, and territorial dominance.

Each team is represented as a multi-dimensional vector — its **Tactical DNA Signature**.

---

## 🧩 Core Components

### 1️⃣ Possession & Passing Features
- Possession share
- Average pass length
- Long pass ratio
- Forward pass ratio
- Circulation tempo

### 2️⃣ Spatial Dominance Modeling
- 5×6 pitch grid (30 zones)
- Zone action distribution
- Average action height (defensive line proxy)
- Width dispersion

### 3️⃣ (Upcoming) Tactical Intelligence Layer
- PCA tactical embedding
- Team similarity scoring
- Clustering
- Radar fingerprint visualization
- Interactive dashboard

---

## 📊 Data Source

- **StatsBomb Open Data**
- Competition: UEFA Champions League (Men)
- Event-level dataset (passes, carries, shots, pressures, recoveries)

⚠️ Raw data is **not included** in this repository due to licensing restrictions.  
Only derived analytics are stored.

---
