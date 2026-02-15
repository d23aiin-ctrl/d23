"""
Repository Interfaces (Ports).

These are abstract interfaces that define how the application
accesses data. Implementations are in the infrastructure layer.

This is the "Dependency Inversion" - domain defines interfaces,
infrastructure implements them.
"""

from .pnr_repository import PNRRepository
from .train_repository import TrainRepository

__all__ = ["PNRRepository", "TrainRepository"]
