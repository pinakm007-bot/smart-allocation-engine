from fastapi import APIRouter
from src.utils import load_bom, load_inventory, load_demand
from src.core import run_allocation, run_scenario, freeze_allocation, execute_allocation

router = APIRouter()


# =========================
# HEALTH CHECK
# =========================
@router.get("/")
def root():
    return {"message": "Smart Allocation API is running"}


# =========================
# RUN ALLOCATION
# =========================
@router.get("/run-allocation")
def run_allocation_api():
    """
    Runs allocation using Excel files
    """

    bom = load_bom("BOM.xlsx")
    inventory = load_inventory("inventory.xlsx")
    demand = load_demand("demand.xlsx")

    result = run_allocation(demand, inventory, bom)

    return {"allocation_result": result}


# =========================
# RUN SCENARIO
# =========================
@router.get("/run-scenario")
def run_scenario_api():
    """
    Runs simple what-if scenario
    """

    bom = load_bom("BOM.xlsx")
    inventory = load_inventory("inventory.xlsx")
    demand = load_demand("demand.xlsx")

    result = run_scenario(demand, inventory, bom)

    return {"scenario_result": result}


# =========================
# FREEZE (TEST)
# =========================
@router.get("/freeze")
def freeze_api():
    """
    Dummy freeze test (for Phase 1)
    """

    bom = load_bom("BOM.xlsx")
    inventory = load_inventory("inventory.xlsx")
    demand = load_demand("demand.xlsx")

    allocation = run_allocation(demand, inventory, bom)

    # Freeze first item partially
    freeze_request = [
        {
            "item_id": allocation[0]["item_id"],
            "qty_to_freeze": allocation[0]["allocated_qty"] // 2
        }
    ]

    frozen = freeze_allocation(allocation, freeze_request)

    return {"frozen": frozen}


# =========================
# EXECUTE
# =========================
@router.get("/execute")
def execute_api():
    """
    Executes allocation and updates inventory
    """

    bom = load_bom("BOM.xlsx")
    inventory = load_inventory("inventory.xlsx")
    demand = load_demand("demand.xlsx")

    allocation = run_allocation(demand, inventory, bom)

    result = execute_allocation(inventory, allocation, bom)

    return result