#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tarfile
from dataclasses import asdict, dataclass, field
from pathlib import Path, PurePosixPath
from typing import Dict, List, Optional, Tuple

WHITEOUT_PREFIX = ".wh."
OPAQUE_MARKER = ".wh..wh..opq"
CHUNK_BYTES = 1 << 20
METADATA_FIELDS = ("mtime", "mode", "owner")


class LayerError(Exception):
    pass


@dataclass(frozen=True)
class Entry:
    kind: str
    content: str
    size: int
    mode: int
    owner: str
    mtime: int


@dataclass
class LayerStats:
    position: int
    path: str
    entries: int
    readded_files: List[str] = field(default_factory=list)
    readded_bytes: int = 0
    readded_metadata: List[str] = field(default_factory=list)


@dataclass
class Comparison:
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    changed: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    mtime_only: List[str] = field(default_factory=list)

    @property
    def equivalent(self) -> bool:
        return not (self.added or self.removed or self.changed or self.permissions)


def normalise(name: str) -> str:
    return "/".join(part for part in PurePosixPath(name).parts if part not in ("/", "."))


def content_of(archive: tarfile.TarFile, member: tarfile.TarInfo) -> Tuple[str, str]:
    if member.isfile():
        digest = hashlib.sha256()
        handle = archive.extractfile(member)
        if handle is None:
            raise LayerError(f"cannot read {member.name}")
        with handle:
            for chunk in iter(lambda: handle.read(CHUNK_BYTES), b""):
                digest.update(chunk)
        return "file", digest.hexdigest()
    if member.issym():
        return "symlink", member.linkname
    if member.islnk():
        return "hardlink", normalise(member.linkname)
    if member.isdir():
        return "dir", ""
    return "other", f"{member.type!r}:{member.devmajor}:{member.devminor}"


def read_layer(path: Path) -> Dict[str, Entry]:
    entries: Dict[str, Entry] = {}
    try:
        with tarfile.open(path, "r:*") as archive:
            for member in archive:
                kind, content = content_of(archive, member)
                entries[normalise(member.name)] = Entry(
                    kind, content, member.size, member.mode, f"{member.uid}:{member.gid}", int(member.mtime))
    except FileNotFoundError as error:
        raise LayerError(f"{path}: no such file") from error
    except (tarfile.TarError, OSError, EOFError) as error:
        raise LayerError(f"{path}: not a readable tar, tar.gz, tar.bz2 or tar.xz layer ({error}); "
                         "decompress a zstd layer with zstd -d first") from error
    return entries


def remove_tree(tree: Dict[str, Entry], root: str, keep_root: bool) -> None:
    prefix = f"{root}/" if root else ""
    for name in [name for name in tree if name.startswith(prefix) or (name == root and not keep_root)]:
        del tree[name]


def differing_metadata(lower: Entry, upper: Entry) -> List[str]:
    return [name for name in METADATA_FIELDS if getattr(lower, name) != getattr(upper, name)]


def apply_layer(tree: Dict[str, Entry], layer: Dict[str, Entry], stats: LayerStats) -> None:
    for name in layer:
        path = PurePosixPath(name)
        if path.name == OPAQUE_MARKER:
            remove_tree(tree, str(path.parent) if str(path.parent) != "." else "", keep_root=True)
        elif path.name.startswith(WHITEOUT_PREFIX):
            target = path.parent / path.name[len(WHITEOUT_PREFIX):]
            remove_tree(tree, str(target), keep_root=False)
    metadata_seen = set()
    for name, entry in layer.items():
        if PurePosixPath(name).name.startswith(WHITEOUT_PREFIX):
            continue
        lower = tree.get(name)
        if lower and entry.kind == "file" and lower.kind == "file" and lower.content == entry.content:
            stats.readded_files.append(name)
            stats.readded_bytes += entry.size
            metadata_seen.update(differing_metadata(lower, entry) or ["nothing"])
        tree[name] = entry
    stats.readded_metadata = sorted(metadata_seen)


def flatten(paths: List[Path]) -> Tuple[Dict[str, Entry], List[LayerStats]]:
    tree: Dict[str, Entry] = {}
    stats = []
    for position, path in enumerate(paths, 1):
        layer = read_layer(path)
        layer_stats = LayerStats(position, str(path), len(layer))
        apply_layer(tree, layer, layer_stats)
        stats.append(layer_stats)
    return tree, stats


def compare(first: Dict[str, Entry], second: Dict[str, Entry]) -> Comparison:
    result = Comparison()
    for name in sorted(set(first) | set(second)):
        old, new = first.get(name), second.get(name)
        if old is None:
            result.added.append(name)
        elif new is None:
            result.removed.append(name)
        elif (old.kind, old.content) != (new.kind, new.content):
            result.changed.append(name)
        elif (old.mode, old.owner) != (new.mode, new.owner):
            result.permissions.append(name)
        elif old.mtime != new.mtime and old.kind != "dir":
            result.mtime_only.append(name)
    return result


def human_bytes(count: int) -> str:
    size = float(count)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{count} B"


def examples(names: List[str], limit: int) -> str:
    shown = ", ".join(names[:limit])
    return shown + (f", and {len(names) - limit} more" if len(names) > limit else "")


def describe_image(label: str, tree: Dict[str, Entry], stats: List[LayerStats], limit: int, out) -> None:
    print(f"image {label}: {len(stats)} layers, {len(tree)} paths in the final tree", file=out)
    for layer in stats:
        line = f"  layer {layer.position} ({Path(layer.path).name}): {layer.entries} entries"
        if layer.readded_files:
            line += (f", re-adds {len(layer.readded_files)} files with unchanged content"
                     f" ({human_bytes(layer.readded_bytes)}; metadata differs in: {', '.join(layer.readded_metadata)})")
        print(line, file=out)
        if layer.readded_files:
            print(f"    e.g. {examples(layer.readded_files, limit)}", file=out)


def describe_comparison(comparison: Comparison, limit: int, out) -> None:
    for label, names in (("added", comparison.added), ("removed", comparison.removed),
                         ("content changed", comparison.changed), ("mode or owner changed", comparison.permissions)):
        if names:
            print(f"  {label}: {len(names)}  {examples(names, limit)}", file=out)
    verdict = "equivalent" if comparison.equivalent else "different"
    noise = f"; {len(comparison.mtime_only)} files differ only in mtime" if comparison.mtime_only else ""
    print(f"final trees: {verdict}{noise}", file=out)


def parse_arguments(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Flatten an image's layer tarballs (base first) and report files a layer re-adds with unchanged "
        "content; with --against, compare the final file trees of two images by content.",
    )
    parser.add_argument("layers", nargs="+", type=Path, help="layer blobs of image A, in manifest order")
    parser.add_argument("--against", nargs="+", type=Path, metavar="LAYER", help="layer blobs of image B, in manifest order")
    parser.add_argument("--examples", type=int, default=5, help="paths to show per category (default 5)")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None, out=sys.stdout, err=sys.stderr) -> int:
    arguments = parse_arguments(sys.argv[1:] if argv is None else argv)
    try:
        tree_a, stats_a = flatten(arguments.layers)
        image_b = flatten(arguments.against) if arguments.against else None
    except LayerError as error:
        print(f"layer_diff: {error}", file=err)
        return 2
    comparison = compare(tree_a, image_b[0]) if image_b else None
    if arguments.json:
        payload = {"a": [asdict(layer) for layer in stats_a]}
        if image_b:
            payload["b"] = [asdict(layer) for layer in image_b[1]]
            payload["comparison"] = dict(asdict(comparison), equivalent=comparison.equivalent)
        json.dump(payload, out, indent=2)
        print("", file=out)
    else:
        describe_image("A", tree_a, stats_a, arguments.examples, out)
        if image_b:
            describe_image("B", image_b[0], image_b[1], arguments.examples, out)
            describe_comparison(comparison, arguments.examples, out)
    return 1 if comparison and not comparison.equivalent else 0


if __name__ == "__main__":
    sys.exit(main())
