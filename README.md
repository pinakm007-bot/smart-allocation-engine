# 🚀 Demand Allocation Engine

## 📄 Overview
The Demand Allocation Engine is a backend application designed to determine production feasibility by allocating available inventory to SKU-level demand based on Bill of Materials (BOM). It enables demand-driven planning by translating SKU requirements into component-level consumption and matching them against available stock.

This system helps identify how much production can be achieved with current inventory and highlights shortages at both component and SKU levels.

---

## 🎯 Objectives
- Enable demand-driven production planning  
- Perform BOM-based requirement calculation  
- Allocate inventory against demand  
- Identify shortages and production feasibility  

---

## 🧱 System Architecture (High-Level)
The system follows a structured processing flow:

1. BOM is uploaded and stored in the database (master data)  
2. Inventory and Demand are provided as runtime inputs (CSV/Excel)  
3. Data is validated against BOM  
4. Requirements are calculated (BOM × Demand)  
5. Allocation logic determines feasible production  
6. Output reports are generated  

---

## ⚙️ Core Services

- **BOM Service**  
  Handles BOM upload, validation, and storage in PostgreSQL  

- **Input Ingestion Service**  
  Reads and parses Inventory and Demand CSV/Excel files  

- **Validation Service**  
  Validates schema, data integrity, and BOM references  

- **Requirement Calculation Service**  
  Converts SKU demand into component-level requirements  

- **Allocation Service**  
  Core engine that matches requirements with available inventory  

---

## 📥 Input Data Format

### Inventory File (CSV/Excel)
