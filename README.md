# simple-filename-collision

Renames files during batch operations so that no two output names collide. The first occurrence of each name is kept unchanged; later duplicates are rewritten according to a pluggable strategy.

## Usage

```python
from simple_filename_collision import CollisionResolver, NumberingStrategy, SuffixStrategy

# Default: append _1, _2, ... before the extension.
resolver = CollisionResolver()
resolver.resolve(["a.txt", "a.txt", "b.txt"])
# → ['a.txt', 'a_1.txt', 'b.txt']

# Or use a suffix scheme that repeats the suffix for each duplicate.
resolver = CollisionResolver(SuffixStrategy("copy"))
resolver.resolve(["a.txt", "a.txt", "a.txt"])
# → ['a.txt', 'a_copy.txt', 'a_copycopy.txt']
```

## Why this exists

When copying or archiving a flat set of files into a single directory, name collisions are inevitable. Doing this with shell tools usually means either silently overwriting or stopping on the first conflict. This library gives a deterministic, in-process way to assign unique names up front, before any file is written, so the caller can plan the full operation first and execute it without surprises.

The trade-off: the library only resolves *within the batch you give it*. It does not look at the target directory on disk, because that would couple a pure function to filesystem state and make testing harder. If you need to avoid colliding with existing files, read the directory first and prepend those names to the input list.

## Edge cases worth knowing

- `os.path.splitext` treats only the last dot as the extension separator, so `archive.tar.gz` becomes `archive.tar_1.gz`, not `archive_1.tar.gz`.
- A leading-dot filename like `.bashrc` is treated as having no extension; the suffix or number is appended directly.
- If a generated candidate already appears among the outputs (e.g. your batch contains both `a.txt` and `a_1.txt`), the resolver bumps the counter until it finds a free slot.
