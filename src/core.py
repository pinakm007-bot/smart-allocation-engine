"""
core.py
Pure business logic for allocation, scenario, freeze, execute.
"""

from typing import List, Dict, Any, Optional


# =========================
# VALIDATION
# =========================
def _validate_inputs(demand: List[Dict], inventory: List[Dict], bom: List[Dict]):
    for d in demand:
        if d.get("required_qty", 0) <= 0:
            raise ValueError(f"Invalid demand for {d.get('item_id')}")

    for i in inventory:
        if i.get("available_qty", 0) < 0:
            raise ValueError(f"Invalid inventory for {i.get('material_id')}")

    for b in bom:
        if not b.get("item_id") or not b.get("material_id"):
            raise ValueError("Invalid BOM entry")


# =========================
# ALLOCATION (BOM BASED)
# =========================
def run_allocation(
    demand: List[Dict[str, Any]],
    inventory: List[Dict[str, Any]],
    bom: List[Dict[str, Any]],
) -> Dict[str, Any]:

    _validate_inputs(demand, inventory, bom)

    inv_map = {i["material_id"]: float(i["available_qty"]) for i in inventory}

    bom_map = {}
    for b in bom:
        bom_map.setdefault(b["item_id"], []).append(b)

    results = []

    # ✅ SUMMARY COUNTERS
    fully_allocated = 0
    partially_allocated = 0
    not_allocated = 0

    for d in demand:
        item_id = d["item_id"]
        required_qty = float(d["required_qty"])

        components = bom_map.get(item_id, [])

        if not components:
            not_allocated += 1
            results.append({
                "item_id": item_id,
                "required_qty": required_qty,
                "allocated_qty": 0,
                "shortfall": required_qty,
                "status": "FAILED",
                "message": "No BOM found"
            })
            continue

        missing_materials = []
        possible_units = float("inf")

        for comp in components:
            mat = comp["material_id"]
            cons = float(comp.get("consumption_qty", 0))

            if cons <= 0:
                possible_units = 0
                break

            available = inv_map.get(mat, 0)

            if available <= 0:
                missing_materials.append(mat)

            units = available / cons
            possible_units = min(possible_units, units)

        if missing_materials:
            not_allocated += 1
            results.append({
                "item_id": item_id,
                "required_qty": required_qty,
                "allocated_qty": 0,
                "shortfall": required_qty,
                "status": "FAILED",
                "message": f"Missing inventory for materials: {list(set(missing_materials))}"
            })
            continue

        possible_units = int(possible_units) if possible_units != float("inf") else 0
        allocated_qty = min(required_qty, possible_units)

        # 🔥 Deduct inventory
        for comp in components:
            mat = comp["material_id"]
            cons = float(comp.get("consumption_qty", 0))

            deduction = allocated_qty * cons
            inv_map[mat] = max(0, inv_map.get(mat, 0) - deduction)

        shortfall = max(0, required_qty - allocated_qty)

        # ✅ Categorize
        if allocated_qty == 0:
            not_allocated += 1
        elif allocated_qty == required_qty:
            fully_allocated += 1
        else:
            partially_allocated += 1

        results.append({
            "item_id": item_id,
            "required_qty": required_qty,
            "allocated_qty": allocated_qty,
            "shortfall": shortfall,
            "status": "SUCCESS"
        })

    # ✅ FINAL SUMMARY
    summary = {
        "total_skus": len(demand),
        "fully_allocated": fully_allocated,
        "partially_allocated": partially_allocated,
        "not_allocated": not_allocated
    }

    return {
        "allocation_result": results,
        "allocation_summary": summary
    }


# =========================
# SCENARIO
# =========================
def run_scenario(
    base_demand: List[Dict],
    base_inventory: List[Dict],
    base_bom: List[Dict],
    modified_demand: Optional[List[Dict]] = None,
    modified_inventory: Optional[List[Dict]] = None
) -> Dict[str, Any]:

    effective_demand = modified_demand if modified_demand else base_demand
    effective_inventory = modified_inventory if modified_inventory else base_inventory

    return run_allocation(effective_demand, effective_inventory, base_bom)


# =========================
# FREEZE
# =========================
def freeze_allocation(
    allocation_results: List[Dict],
    freeze_requests: List[Dict]
) -> List[Dict]:

    allocated_map = {r["item_id"]: r["allocated_qty"] for r in allocation_results}

    frozen = []

    for f in freeze_requests:
        item_id = f["item_id"]
        qty = f["qty_to_freeze"]

        if item_id not in allocated_map:
            raise ValueError(f"{item_id} not found")

        if qty > allocated_map[item_id]:
            raise ValueError(f"Freeze exceeds allocation for {item_id}")

        frozen.append({
            "item_id": item_id,
            "frozen_qty": qty
        })

    return frozen


# =========================
# EXECUTE
# =========================
def execute_allocation(
    inventory: List[Dict],
    allocation_results: List[Dict],
    bom: List[Dict],
    frozen_items: Optional[List[Dict]] = None
) -> Dict[str, Any]:

    if frozen_items:
        commit_map = {f["item_id"]: f["frozen_qty"] for f in frozen_items}
    else:
        commit_map = {a["item_id"]: a["allocated_qty"] for a in allocation_results}

    bom_map = {}
    for b in bom:
        bom_map.setdefault(b["item_id"], []).append(b)

    inv_map = {i["material_id"]: float(i["available_qty"]) for i in inventory}

    total_consumed = 0.0

    for item_id, qty in commit_map.items():
        for comp in bom_map.get(item_id, []):
            mat = comp["material_id"]
            cons = float(comp.get("consumption_qty", 0))

            deduction = qty * cons
            inv_map[mat] = max(0, inv_map.get(mat, 0) - deduction)

            total_consumed += deduction

    updated_inventory = [
        {"material_id": k, "remaining_qty": v}
        for k, v in inv_map.items()
    ]

    # ✅ INVENTORY SUMMARY
    inventory_summary = {
        "total_materials": len(inv_map),
        "total_material_consumed": total_consumed,
        "materials_remaining": sum(inv_map.values())
    }

    return {
        "updated_inventory": updated_inventory,
        "inventory_summary": inventory_summary
    }