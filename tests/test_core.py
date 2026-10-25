import os
import unittest

from simple_filename_collision.core import (
    CollisionResolver,
    NumberingStrategy,
    SuffixStrategy,
)


class TestNumberingStrategy(unittest.TestCase):
    def test_single_extension(self):
        s = NumberingStrategy()
        self.assertEqual(s.next_candidate("file.txt", 0), "file_1.txt")
        self.assertEqual(s.next_candidate("file.txt", 1), "file_2.txt")

    def test_no_extension(self):
        s = NumberingStrategy()
        self.assertEqual(s.next_candidate("README", 0), "README_1")

    def test_multiple_dots(self):
        s = NumberingStrategy()
        # os.path.splitext only treats the last dot as the separator.
        self.assertEqual(s.next_candidate("archive.tar.gz", 0), "archive.tar_1.gz")

    def test_dotfile(self):
        s = NumberingStrategy()
        # os.path.splitext treats leading-dot files as having no stem.
        self.assertEqual(s.next_candidate(".bashrc", 0), ".bashrc_1")


class TestSuffixStrategy(unittest.TestCase):
    def test_default_suffix(self):
        s = SuffixStrategy()
        self.assertEqual(s.next_candidate("file.txt", 0), "file_copy.txt")
        self.assertEqual(s.next_candidate("file.txt", 1), "file_copycopy.txt")

    def test_custom_suffix(self):
        s = SuffixStrategy(suffix="dup")
        self.assertEqual(s.next_candidate("file.txt", 0), "file_dup.txt")

    def test_empty_suffix_rejected(self):
        with self.assertRaises(ValueError):
            SuffixStrategy(suffix="")


class TestCollisionResolver(unittest.TestCase):
    def test_no_duplicates(self):
        r = CollisionResolver()
        self.assertEqual(r.resolve(["a.txt", "b.txt"]), ["a.txt", "b.txt"])

    def test_single_duplicate(self):
        r = CollisionResolver()
        self.assertEqual(
            r.resolve(["a.txt", "a.txt"]),
            ["a.txt", "a_1.txt"],
        )

    def test_many_duplicates(self):
        r = CollisionResolver()
        out = r.resolve(["a.txt"] * 3)
        self.assertEqual(out, ["a.txt", "a_1.txt", "a_2.txt"])

    def test_suffix_strategy_in_resolver(self):
        r = CollisionResolver(SuffixStrategy("copy"))
        out = r.resolve(["a.txt", "a.txt"])
        self.assertEqual(out, ["a.txt", "a_copy.txt"])

    def test_overlapping_names(self):
        # If the first duplicate's generated name collides with an existing
        # output entry, the resolver should skip past it.
        r = CollisionResolver(NumberingStrategy())
        out = r.resolve(["a.txt", "a_1.txt", "a.txt"])
        self.assertEqual(out, ["a.txt", "a_1.txt", "a_2.txt"])

    def test_empty_list(self):
        r = CollisionResolver()
        self.assertEqual(r.resolve([]), [])

    def test_preserves_order(self):
        r = CollisionResolver()
        out = r.resolve(["a.txt", "b.txt", "a.txt", "b.txt"])
        self.assertEqual(out, ["a.txt", "b.txt", "a_1.txt", "b_1.txt"])


if __name__ == "__main__":
    unittest.main()
