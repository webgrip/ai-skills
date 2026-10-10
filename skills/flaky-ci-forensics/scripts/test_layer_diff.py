import importlib.util
import io
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("layer_diff", HERE / "layer_diff.py")
layer_diff = importlib.util.module_from_spec(spec)
sys.modules["layer_diff"] = layer_diff
spec.loader.exec_module(layer_diff)

EARLY, LATE = 1_700_000_000, 1_700_086_400


def write_layer(path, members):
    with tarfile.open(path, "w:gz") as archive:
        for name, (content, mtime, mode) in members.items():
            info = tarfile.TarInfo(name)
            info.mtime, info.mode = mtime, mode
            if content is None:
                info.type = tarfile.DIRTYPE
                archive.addfile(info)
            else:
                data = content.encode()
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
    return str(path)


def file(content, mtime=EARLY, mode=0o644):
    return (content, mtime, mode)


def directory(mtime=EARLY):
    return (None, mtime, 0o755)


def run(arguments):
    out, err = io.StringIO(), io.StringIO()
    code = layer_diff.main(arguments, out=out, err=err)
    return code, out.getvalue(), err.getvalue()


class LayerDiffTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.dependencies = write_layer(self.root / "a1.tar.gz", {
            "./app/": directory(), "./app/composer.json": file("{}"), "./app/composer.lock": file("lock")})
        self.sources_a = write_layer(self.root / "a2.tar.gz", {
            "./app/src/": directory(), "./app/src/Order.php": file("<?php class Order {}"), "./app/.env.example": file("APP_ENV=")})

    def tearDown(self):
        self.temporary.cleanup()

    def image_b(self, sources):
        return [self.dependencies, write_layer(self.root / "b2.tar.gz", sources)]

    def buildkit_rebuild(self, **changes):
        sources = {
            "./app/": directory(LATE),
            "./app/composer.json": file("{}", LATE),
            "./app/composer.lock": file("lock", LATE),
            "./app/src/": directory(LATE),
            "./app/src/Order.php": file("<?php class Order {}", LATE),
            "./app/.env.example": file("APP_ENV=", LATE),
        }
        sources.update(changes)
        return self.image_b(sources)

    def test_same_content_with_new_mtimes_is_equivalent_and_the_readds_are_named(self):
        code, out, _ = run([self.dependencies, self.sources_a, "--against"] + self.buildkit_rebuild())
        self.assertEqual(code, 0)
        self.assertIn("layer 2 (b2.tar.gz): 6 entries, re-adds 2 files with unchanged content (6 B; metadata differs in: mtime)", out)
        self.assertIn("e.g. app/composer.json, app/composer.lock", out)
        self.assertIn("final trees: equivalent; 4 files differ only in mtime", out)

    def test_changed_content_is_different(self):
        code, out, _ = run([self.dependencies, self.sources_a, "--against"]
                           + self.buildkit_rebuild(**{"./app/src/Order.php": file("<?php class Order { public $id; }", LATE)}))
        self.assertEqual(code, 1)
        self.assertIn("content changed: 1  app/src/Order.php", out)
        self.assertIn("final trees: different", out)

    def test_whiteout_removes_a_lower_file(self):
        code, out, _ = run([self.dependencies, self.sources_a, "--against"]
                           + self.image_b({"./app/src/": directory(), "./app/src/Order.php": file("<?php class Order {}"),
                                           "./app/.env.example": file("APP_ENV="), "./app/.wh.composer.lock": file("")}))
        self.assertEqual(code, 1)
        self.assertIn("removed: 1  app/composer.lock", out)

    def test_opaque_directory_hides_the_lower_contents(self):
        code, out, _ = run([self.dependencies, self.sources_a, "--against"]
                           + self.image_b({"./app/.wh..wh..opq": file(""), "./app/src/": directory(),
                                           "./app/src/Order.php": file("<?php class Order {}"), "./app/.env.example": file("APP_ENV=")}))
        self.assertEqual(code, 1)
        self.assertIn("removed: 2  app/composer.json, app/composer.lock", out)

    def test_mode_change_is_a_real_difference(self):
        code, out, _ = run([self.dependencies, self.sources_a, "--against"]
                           + self.buildkit_rebuild(**{"./app/src/Order.php": file("<?php class Order {}", LATE, 0o755)}))
        self.assertEqual(code, 1)
        self.assertIn("mode or owner changed: 1  app/src/Order.php", out)

    def test_single_image_reports_readds_and_exits_zero(self):
        code, out, _ = run(self.buildkit_rebuild() + ["--json"])
        report = json.loads(out)
        self.assertEqual(code, 0)
        self.assertEqual(report["a"][1]["readded_files"], ["app/composer.json", "app/composer.lock"])
        self.assertNotIn("comparison", report)

    def test_identical_images_report_nothing_readded(self):
        code, out, _ = run([self.dependencies, self.sources_a, "--against", self.dependencies, self.sources_a])
        self.assertEqual(code, 0)
        self.assertNotIn("re-adds", out)
        self.assertIn("final trees: equivalent\n", out)

    def test_not_a_tar_is_an_error(self):
        broken = self.root / "layer.tar.zst"
        broken.write_bytes(b"\x28\xb5\x2f\xfd not really zstd")
        code, _, err = run([str(broken)])
        self.assertEqual(code, 2)
        self.assertIn("zstd -d", err)

    def test_hidden_file_names_keep_their_dot(self):
        self.assertEqual(layer_diff.normalise("./.env"), ".env")
        self.assertEqual(layer_diff.normalise("/app/./src/"), "app/src")


if __name__ == "__main__":
    unittest.main()
