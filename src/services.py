"""
services.py
Orchestration layer that connects API routes to core business logic.
Handles state management (in-memory) and UUID generation.
"""

import uuid
from typing import List, Dict, Any, Optional
from core import (
    run_allocation,
    run_scenario,
    freeze_allocation,
    execute_allocation
)

# In-memory storage to simulate a database
# Structure: { allocation_id: { "results": [], "inventory": [], "frozen": [] } }
ALLOCATION_STORE: Dict[str, Dict[str, Any]] = {}


async def allocation_service(
    demand: List[Dict], 
    inventory: List[Dict], 
    allocation_type: str
) -> Dict[str, Any]:
    """
    Orchestrates a new allocation run.
    Generates a unique ID and persists the results for later freeze/execution.
    """
    # 1. Call core logic
    results = run_allocation(demand, inventory, allocation_type)
    
    # 2. Generate unique reference
    allocation_id = str(uuid.uuid4())
    
    # 3. Store the context (required for execution later)
    ALLOCATION_STORE[allocation_id] = {
        "results": results,
        "inventory": inventory,
        "frozen": None
    }
    
    return {
        "allocation_id": allocation_id,
        "details": results
    }


async def scenario_service(
    modified_demand: Optional[List[Dict]] = None, 
    modified_inventory: Optional[List[Dict]] = None
) -> List[Dict]:
    """
    Runs a simulation. Unlike the standard allocation, 
    this is transient and NOT stored in the ALLOCATION_STORE.
    """
    # In a real app, you might fetch 'base' data from a DB here.
    # For now, we treat the scenario as an independent calculation.
    return run_scenario(
        base_demand=[], 
        base_inventory=[], 
        modified_demand=modified_demand, 
        modified_inventory=modified_inventory
    )


async def freeze_service(
    allocation_id: str, 
    freeze_items: List[Dict]
) -> List[Dict]:
    """
    Validates the existence of an allocation and applies freeze logic.
    Updates the stored allocation with frozen quantities.
    """
    # 1. Check if allocation exists
    if allocation_id not in ALLOCATION_STORE:
        raise ValueError(f"Allocation reference '{allocation_id}' not found.")
    
    # 2. Retrieve the results from the previous run
    stored_data = ALLOCATION_STORE[allocation_id]
    
    # 3. Apply freeze logic
    # Expected core input: (allocation_results, freeze_requests)
    frozen_data = freeze_allocation(stored_data["results"], freeze_items)
    
    # 4. Update the store with the frozen quantities
    ALLOCATION_STORE[allocation_id]["frozen"] = frozen_data
    
    return frozen_data


async def execution_service(allocation_id: str) -> Dict[str, Any]:
    """
    Finalizes an allocation. Deducts stock and clears the record from the active store.
    """
    # 1. Check if allocation exists
    if allocation_id not in ALLOCATION_STORE:
        raise LookupError(f"Allocation '{allocation_id}' does not exist or was already executed.")
    
    data = ALLOCATION_STORE[allocation_id]
    
    # 2. Call execution logic
    # core.execute_allocation(inventory, allocation_results, frozen_items)
    summary = execute_allocation(
        data["inventory"], 
        data["results"], 
        data.get("frozen")
    )
    
    # 3. Cleanup: In a real system, you'd move this to an 'Archive' or 'Transactions' table.
    # Here, we just remove it from our in-memory store.
    del ALLOCATION_STORE[allocation_id]
    
    return summary


def get_all_active_allocations() -> List[str]:
    """Helper to list IDs currently in memory (useful for debugging)."""
    return list(ALLOCATION_STORE.keys())
