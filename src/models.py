"""
models.py
Defines the data structures for Demand, Inventory, BOM, and Allocation results.
Uses Pydantic for validation and serialization.
"""

from typing import List
from pydantic import BaseModel, Field


class DemandItem(BaseModel):
    """Represents a single line of demand for a finished item."""
    item_id: str = Field(..., description="Unique identifier for the end product")
    required_qty: float = Field(..., gt=0, description="Quantity requested; must be greater than zero")


class InventoryItem(BaseModel):
    """Represents available raw material or fabric in stock."""
    material_id: str = Field(..., description="Unique identifier for the raw material")
    available_qty: float = Field(..., ge=0, description="Quantity in stock; must be 0 or greater")


class BOMItem(BaseModel):
    """Defines the relationship between an item and the material required to make it."""
    item_id: str = Field(..., description="Identifier for the finished item")
    material_id: str = Field(..., description="Identifier for the material required")
    consumption_qty: float = Field(..., gt=0, description="Amount of material needed per unit of item")


class AllocationDetail(BaseModel):
    """The result of an allocation calculation for a specific demand item."""
    item_id: str
    required_qty: float = Field(..., gt=0)
    allocated_qty: float = Field(..., ge=0)
    
    @property
    def shortfall(self) -> float:
        """Calculates the difference between required and allocated."""
        return max(0.0, self.required_qty - self.allocated_qty)


class AllocationResult(BaseModel):
    """A collection of allocation details representing a full run."""
    allocation_id: str = Field(..., description="Unique UUID or reference for this run")
    details: List[AllocationDetail]


class FreezeItem(BaseModel):
    """Represents a quantity of an item that has been locked/confirmed."""
    item_id: str
    frozen_qty: float = Field(..., ge=0, description="The specific quantity to lock against this item")


class InventoryTransaction(BaseModel):
    """Helper model to show changes in inventory during execution."""
    material_id: str
    previous_qty: float
    deducted_qty: float
    remaining_qty: float


class ExecutionSummary(BaseModel):
    """The final report generated after an allocation is committed/executed."""
    allocation_id: str
    consumed_inventory: List[InventoryTransaction] = Field(
        ..., description="List of materials and the amounts deducted"
    )
    remaining_inventory: List[InventoryItem] = Field(
        ..., description="Snapshot of inventory levels after execution"
    )
