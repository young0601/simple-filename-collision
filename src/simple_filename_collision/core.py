"""Core resolution logic for filename collisions.

The module is intentionally small: it takes a sequence of desired filenames
and returns a parallel list of non-conflicting names.  The two supported
strategies share a base class so that users can write their own by
sub-classing :class:`ResolutionStrategy`.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Dict, List, Sequence


class ResolutionStrategy(ABC):
    """Base class for name-conflict strategies.

    A strategy produces a candidate replacement name for the *first*
    duplicate of ``original``.  Subsequent duplicates of the same original
    call :meth:`next_candidate` again, so strategies that need a counter
    (e.g. numbering) must track state per original-name.

    Using an abstract base class keeps the public contract explicit and
    lets users plug in custom strategies without monkey-patching.
    """

    @abstractmethod
    def next_candidate(self, original: str, index: int) -> str:
        """Return a candidate name for the *index*-th duplicate of *original*.

        ``index`` is zero-based: 0 is the first duplicate, 1 the second, etc.
        The original file is **not** passed here; it keeps its name unchanged.
        """
        raise NotImplementedError


class NumberingStrategy(ResolutionStrategy):
    """Append ``_1``, ``_2`` … before the extension.

    If the generated candidate already exists in the output set, the caller
    bumps ``index`` until a free slot is found.  This means we never silently
    overwrite an existing numbered file.
    """

    def next_candidate(self, original: str, index: int) -> str:
        stem, ext = os.path.splitext(original)
        # index+1 so the first duplicate becomes name_1, not name_0.
        return f"{stem}_{index + 1}{ext}"


class SuffixStrategy(ResolutionStrategy):
    """Append a fixed suffix before the extension.

    Each duplicate gets an extra copy of the suffix, so ``copy`` → ``copy_copy``
    → ``copy_copy_copy``.  This keeps the scheme parameter-free while still
    producing unique names.
    """

    def __init__(self, suffix: str = "copy") -> None:
        if not suffix:
            raise ValueError("suffix must be non-empty")
        self.suffix = suffix

    def next_candidate(self, original: str, index: int) -> str:
        stem, ext = os.path.splitext(original)
        # Repeat suffix (index + 1) times: first duplicate gets one suffix.
        return f"{stem}_{self.suffix * (index + 1)}{ext}"


class CollisionResolver:
    """Renames a batch of filenames so the result contains no duplicates.

    The resolver preserves order: the first occurrence of each name keeps
    its original name; only subsequent duplicates are altered.
    """

    def __init__(self, strategy: ResolutionStrategy | None = None) -> None:
        self.strategy = strategy if strategy is not None else NumberingStrategy()

    def resolve(self, names: Sequence[str]) -> List[str]:
        """Return a list of unique names, parallel to *names*.

        Raises :class:`RuntimeError` if no free candidate can be found for a
        name within a generous search bound (10 000 attempts).  This guards
        against pathological inputs that would otherwise loop forever.
        """
        seen: Dict[str, int] = {}
        result: List[str] = []
        max_attempts = 10_000

        for name in names:
            if name not in seen:
                seen[name] = 0
                result.append(name)
                continue

            stem, ext = os.path.splitext(name)
            candidate = None
            for attempt in range(max_attempts):
                candidate = self.strategy.next_candidate(name, seen[name] + attempt)
                if candidate not in seen:
                    break
            else:
                raise RuntimeError(
                    f"Could not find a free name for {name!r} within {max_attempts} attempts"
                )

            # candidate is guaranteed assigned because range(max_attempts) is non-empty.
            assert candidate is not None
            seen[candidate] = 0
            seen[name] += 1
            result.append(candidate)

        return result
