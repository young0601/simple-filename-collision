"""simple-filename-collision: resolve filename conflicts during batch operations."""

from .core import CollisionResolver, ResolutionStrategy, NumberingStrategy, SuffixStrategy

__all__ = [
    "CollisionResolver",
    "ResolutionStrategy",
    "NumberingStrategy",
    "SuffixStrategy",
]
