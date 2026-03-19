import pandas as pd
import os
from typing import List, Dict, Any


# Base directory (src/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def clean_str(value):
    """Clean string values (remove spaces + normalize case)"""
    if value is None:
        return ""
    return str(value).strip().upper()


def load_excel(file_path: str) -> List[Dict[str, Any]]:
    """
    Generic Excel loader.
    """
    full_path = os.path.join(BASE_DIR, file_path)

    try:
        df = pd.read_excel(full_path)
        df.columns = df.columns.str.strip()
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"Error loading file {full_path}: {str(e)} - utils.py:35")
        return []   # safe fallback


# =========================
# BOM
# =========================
def load_bom(file_path: str) -> List[Dict[str, Any]]:
    data = load_excel(file_path)

    standardized = []
    for row in data:
        standardized.append({
            "item_id": clean_str(
                row.get("Item.#.") or row.get("Item") or row.get("SKU")
            ),
            "material_id": clean_str(
                row.get("Fabric.#") or row.get("Fabric") or row.get("Material")
            ),
            "consumption_qty": safe_float(
                row.get("Per.Pc.Cons") or row.get("Consumption")
            )
        })

    return standardized


# =========================
# INVENTORY
# =========================
def load_inventory(file_path: str) -> List[Dict[str, Any]]:
    data = load_excel(file_path)

    standardized = []
    for row in data:
        standardized.append({
            "material_id": clean_str(
                row.get("Fabric") or row.get("Material")
            ),
            "available_qty": safe_float(
                row.get("Stock in Hand") or row.get("Available") or row.get("Stock")
            )
        })

    return standardized


# =========================
# DEMAND
# =========================
def load_demand(file_path: str) -> List[Dict[str, Any]]:
    data = load_excel(file_path)

    standardized = []
    for row in data:
        standardized.append({
            "item_id": clean_str(
                row.get("It3m.#") or row.get("Item.#.") or row.get("Item") or row.get("SKU")
            ),
            "required_qty": safe_float(
                row.get("Qty") or row.get("Demand")
            )
        })

    return standardized