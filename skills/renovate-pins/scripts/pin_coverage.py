#!/usr/bin/env python3
import argparse
import fnmatch
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Set, Tuple

EXIT_CLEAN = 0
EXIT_FINDINGS = 1
EXIT_USAGE = 2

MAX_FILE_BYTES = 2_000_000
SKIPPED_DIRECTORIES = {".git", "node_modules", "vendor", ".venv", "venv", "dist", "build", ".terraform", "__pycache__"}
TEST_DIRECTORIES = {"tests", "test", "testdata", "fixtures", "__fixtures__", "__tests__"}
NOT_PIN_FILE_PATTERNS = ("*.lock", "*.lockb", "*-lock.json", "*-lock.yaml", "*.lock.json", "*.lock.hcl", "go.sum",
                         "requirements*.txt", "*.sum", "*.md", "*.rst", "*.adoc")
INTENTIONAL_SKIP_REASONS = {"package-rules", "ignored", "disabled", "local", "local-chart", "local-dependency",
                            "path-dependency", "file", "file-dependency", "internal-package", "inherited-dependency",
                            "lockfile-only"}
RUN_ENVIRONMENT_SKIP_REASONS = {"github-token-required"}
YAML_SUFFIXES = (".yaml", ".yml")
IMAGE_KEYS = {"image", "imageName"}
REPOSITORY_KEYS = {"repository"}
VERSION_KEYS = {"tag", "version"}
DOCKER_HUB_PREFIXES = ("docker.io/", "index.docker.io/", "registry-1.docker.io/")
OPERATOR_VERSION_FIELDS: Sequence[Tuple[str, str, Tuple[str, ...]]] = (
    ("grafana.integreatly.org/", "Grafana", ("version",)),
    ("monitoring.coreos.com/", "Prometheus", ("version", "image")),
    ("monitoring.coreos.com/", "PrometheusAgent", ("version", "image")),
    ("monitoring.coreos.com/", "Alertmanager", ("version", "image")),
    ("postgresql.cnpg.io/", "Cluster", ("imageName", "imageCatalogRef")),
)

DIGEST = re.compile(r"sha256:[a-f0-9]{64}")
YAML_KEY_VALUE = re.compile(r"^(?P<indent>\s*)(?:-\s+)?(?P<key>[A-Za-z_][\w.-]*)\s*:\s*(?P<value>.*?)\s*$")
DOCKERFILE_FROM = re.compile(r"^\s*FROM\s+(?:--platform=\S+\s+)?(?P<ref>\S+)(?:\s+AS\s+(?P<stage>\S+))?", re.I)
VERSION_LIKE = re.compile(r"\d")
TEMPLATE_MARKERS = ("{{", "${", "$(", "<", "%")


@dataclass(frozen=True)
class Finding:
    severity: str
    rule: str
    path: str
    line: int
    message: str


@dataclass
class ExtractedDependency:
    manager: str
    dep_name: str
    current_value: str
    current_digest: str
    replace_string: str
    skip_reason: str


@dataclass
class YamlEntry:
    line: int
    indent: int
    key: str
    value: str


@dataclass
class Coverage:
    by_file: Dict[str, List[ExtractedDependency]] = field(default_factory=dict)
    needs_token: int = 0

    def deps(self, path: str) -> List[ExtractedDependency]:
        return self.by_file.get(path, [])

    def owns_digest(self, path: str, digest: str) -> bool:
        return any(digest in (dep.current_digest, dep.current_value) or digest in dep.replace_string
                   for dep in self.deps(path))

    def owns_version(self, path: str, name: Optional[str], version: str) -> bool:
        return any(dep.current_value == version and (name is None or names_match(dep.dep_name, name))
                   for dep in self.deps(path))


def normalize_image_name(name: str) -> str:
    for prefix in DOCKER_HUB_PREFIXES:
        if name.startswith(prefix):
            name = name[len(prefix):]
    if name.startswith("library/"):
        name = name[len("library/"):]
    return name


def names_match(extracted: str, found: str) -> bool:
    left, right = normalize_image_name(extracted), normalize_image_name(found)
    return left == right or left.endswith("/" + right) or right.endswith("/" + left)


def split_image_reference(reference: str) -> Tuple[str, Optional[str], Optional[str]]:
    remainder, _, digest = reference.partition("@")
    name, colon, tag = remainder.rpartition(":")
    if not colon or "/" in tag:
        return remainder, None, digest or None
    return name, tag, digest or None


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def strip_trailing_comment(value: str) -> str:
    if value and value[0] in "'\"":
        closing = value.find(value[0], 1)
        return value[:closing + 1] if closing > 0 else value
    return re.split(r"\s+#", value, maxsplit=1)[0]


def is_templated(value: str) -> bool:
    return any(marker in value for marker in TEMPLATE_MARKERS)


def load_coverage(report_path: Path) -> Tuple[Coverage, List[Finding]]:
    report = json.loads(report_path.read_text())
    repositories = report.get("repositories")
    if not isinstance(repositories, dict) or not repositories:
        raise ValueError("report has no repositories; run Renovate with --report-type=file")
    coverage = Coverage()
    findings: List[Finding] = []
    for repository in repositories.values():
        for manager, package_files in (repository.get("packageFiles") or {}).items():
            for package_file in package_files or []:
                path = package_file.get("packageFile", "")
                for dep in package_file.get("deps") or []:
                    extracted = ExtractedDependency(
                        manager=manager,
                        dep_name=str(dep.get("depName") or dep.get("packageName") or ""),
                        current_value=str(dep.get("currentValue") or ""),
                        current_digest=str(dep.get("currentDigest") or ""),
                        replace_string=str(dep.get("replaceString") or ""),
                        skip_reason=str(dep.get("skipReason") or ""),
                    )
                    coverage.by_file.setdefault(path, []).append(extracted)
                    if extracted.skip_reason in RUN_ENVIRONMENT_SKIP_REASONS:
                        coverage.needs_token += 1
                    elif extracted.skip_reason and extracted.skip_reason not in INTENTIONAL_SKIP_REASONS:
                        findings.append(Finding(
                            "warn", "skipped-dependency", path, 0,
                            f"{manager} extracted {extracted.dep_name or '(no name)'} but will not update it "
                            f"(skipReason {extracted.skip_reason})"))
    return coverage, findings


def is_excluded(relative: str, patterns: Iterable[str]) -> bool:
    name = os.path.basename(relative)
    return any(fnmatch.fnmatch(relative, pattern) or fnmatch.fnmatch(name, pattern) for pattern in patterns)


def candidate_files(root: Path, excludes: Sequence[str], skip: Set[Path],
                    include_tests: bool) -> Iterator[Tuple[str, str]]:
    pruned = SKIPPED_DIRECTORIES if include_tests else SKIPPED_DIRECTORIES | TEST_DIRECTORIES
    for directory, subdirectories, files in os.walk(root):
        subdirectories[:] = sorted(d for d in subdirectories if d not in pruned)
        for name in sorted(files):
            path = Path(directory) / name
            relative = path.relative_to(root).as_posix()
            if path.resolve() in skip or is_excluded(relative, NOT_PIN_FILE_PATTERNS) or is_excluded(relative, excludes):
                continue
            try:
                if path.stat().st_size > MAX_FILE_BYTES:
                    continue
                raw = path.read_bytes()
            except OSError:
                continue
            if b"\0" in raw:
                continue
            try:
                yield relative, raw.decode("utf-8")
            except UnicodeDecodeError:
                continue


def is_placeholder_digest(digest: str) -> bool:
    return len(set(digest[len("sha256:"):])) == 1


def digest_findings(path: str, text: str, coverage: Coverage) -> List[Finding]:
    findings = []
    for number, line in enumerate(text.splitlines(), start=1):
        for digest in DIGEST.findall(line):
            if not is_placeholder_digest(digest) and not coverage.owns_digest(path, digest):
                findings.append(Finding("error", "unowned-digest", path, number,
                                        f"{digest[:19]}… is pinned here but no Renovate dependency in this file "
                                        "carries it, so it never moves"))
    return findings


def yaml_entries(lines: Sequence[str]) -> List[YamlEntry]:
    entries = []
    for number, line in enumerate(lines, start=1):
        if line.lstrip().startswith("#"):
            continue
        match = YAML_KEY_VALUE.match(line)
        if match:
            indent = len(match.group("indent")) + (2 if line.lstrip().startswith("- ") else 0)
            value = unquote(strip_trailing_comment(match.group("value")))
            entries.append(YamlEntry(number, indent, match.group("key"), value))
    return entries


def siblings(entries: Sequence[YamlEntry], index: int) -> List[YamlEntry]:
    anchor = entries[index]
    found = []
    for step in (-1, 1):
        position = index + step
        while 0 <= position < len(entries) and entries[position].indent >= anchor.indent:
            if entries[position].indent == anchor.indent:
                found.append(entries[position])
            position += step
    return found


def scalar(value: str) -> bool:
    return bool(value) and value[0] not in "{[|>&*!" and not is_templated(value) and " " not in value


def image_findings(path: str, entries: Sequence[YamlEntry], coverage: Coverage) -> List[Finding]:
    findings = []
    for index, entry in enumerate(entries):
        if not scalar(entry.value):
            continue
        if entry.key in IMAGE_KEYS:
            name, tag, digest = split_image_reference(entry.value)
            if digest and is_placeholder_digest(digest):
                continue
            if tag and VERSION_LIKE.search(tag) and not coverage.owns_version(path, name, tag):
                findings.append(Finding("error", "unowned-image", path, entry.line,
                                        f"{entry.value} is pinned here but no Renovate dependency in this file "
                                        "covers it"))
            if tag or digest:
                continue
        if entry.key in REPOSITORY_KEYS or entry.key in IMAGE_KEYS:
            for sibling in siblings(entries, index):
                if sibling.key in VERSION_KEYS and scalar(sibling.value) and VERSION_LIKE.search(sibling.value):
                    version = sibling.value.split("@")[0]
                    if not coverage.owns_version(path, entry.value, version):
                        findings.append(Finding("error", "unowned-tag", path, sibling.line,
                                                f"{entry.value} {sibling.key} {version} is pinned here but no "
                                                "Renovate dependency in this file covers it"))
    return findings


def yaml_documents(lines: Sequence[str]) -> Iterator[Tuple[int, List[str]]]:
    start, current = 0, []
    for number, line in enumerate(lines):
        if line.startswith("---"):
            if current:
                yield start, current
            start, current = number + 1, []
        else:
            current.append(line)
    if current:
        yield start, current


def spec_children(entries: Sequence[YamlEntry]) -> Optional[List[YamlEntry]]:
    for index, entry in enumerate(entries):
        if entry.indent == 0 and entry.key == "spec":
            children = []
            child_indent = None
            for child in entries[index + 1:]:
                if child.indent == 0:
                    break
                child_indent = child.indent if child_indent is None else child_indent
                if child.indent == child_indent:
                    children.append(child)
            return children
    return None


def is_patch_file(path: str) -> bool:
    return "patch" in os.path.basename(path).lower()


def operator_findings(path: str, lines: Sequence[str], coverage: Coverage) -> List[Finding]:
    findings = []
    if is_patch_file(path):
        return findings
    for offset, document in yaml_documents(lines):
        entries = [YamlEntry(e.line + offset, e.indent, e.key, e.value) for e in yaml_entries(document)]
        top = {e.key: e for e in entries if e.indent == 0}
        api_version, kind = top.get("apiVersion"), top.get("kind")
        if not api_version or not kind:
            continue
        for group, kind_name, version_keys in OPERATOR_VERSION_FIELDS:
            if kind.value != kind_name or not api_version.value.startswith(group):
                continue
            children = spec_children(entries) or []
            pinned = [child for child in children if child.key in version_keys]
            if not pinned:
                findings.append(Finding("warn", "operator-default-version", path, kind.line,
                                        f"{kind_name} sets none of spec.{', spec.'.join(version_keys)}, so it runs "
                                        "whatever version the operator defaults to and no dependency bot sees it"))
                continue
            for child in pinned:
                bare_version = scalar(child.value) and "/" not in child.value and ":" not in child.value
                if bare_version and not coverage.owns_version(path, None, child.value):
                    findings.append(Finding("error", "unowned-operator-version", path, child.line,
                                            f"{kind_name} spec.{child.key} {child.value} is pinned here but no "
                                            "Renovate dependency in this file covers it"))
    return findings


def dockerfile_findings(path: str, lines: Sequence[str], coverage: Coverage) -> List[Finding]:
    findings = []
    stages: Set[str] = set()
    for number, line in enumerate(lines, start=1):
        match = DOCKERFILE_FROM.match(line)
        if not match:
            continue
        reference = match.group("ref")
        if match.group("stage"):
            stages.add(match.group("stage").lower())
        if reference.lower() in stages or reference == "scratch" or is_templated(reference):
            continue
        name, tag, digest = split_image_reference(reference)
        if digest and is_placeholder_digest(digest):
            continue
        if tag and not coverage.owns_version(path, name, tag):
            findings.append(Finding("error", "unowned-image", path, number,
                                    f"FROM {reference} is pinned here but no Renovate dependency in this file "
                                    "covers it"))
    return findings


def is_dockerfile(path: str) -> bool:
    name = os.path.basename(path)
    return name in ("Dockerfile", "Containerfile") or name.startswith("Dockerfile.") or name.endswith(".Dockerfile")


def scan(root: Path, coverage: Coverage, excludes: Sequence[str], skip: Set[Path],
         include_tests: bool) -> List[Finding]:
    findings: List[Finding] = []
    for path, text in candidate_files(root, excludes, skip, include_tests):
        findings.extend(digest_findings(path, text, coverage))
        lines = text.splitlines()
        if path.endswith(YAML_SUFFIXES):
            findings.extend(image_findings(path, yaml_entries(lines), coverage))
            findings.extend(operator_findings(path, lines, coverage))
        elif is_dockerfile(path):
            findings.extend(dockerfile_findings(path, lines, coverage))
    return findings


def deduplicated(findings: Iterable[Finding]) -> List[Finding]:
    seen: Set[Tuple[str, int, str, str]] = set()
    unique = []
    for finding in sorted(findings, key=lambda f: (f.path, f.line, f.rule, f.message)):
        key = (finding.path, finding.line, finding.rule, finding.message)
        if key not in seen:
            seen.add(key)
            unique.append(finding)
    return unique


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare the pins in a repository with the dependencies Renovate extracted, and list every pin "
        "Renovate does not see. Exit 0: every pin is covered; 1: findings; 2: usage error.")
    parser.add_argument("--report", required=True, type=Path,
                        help="Renovate report from --platform=local --dry-run=extract --report-type=file")
    parser.add_argument("--root", type=Path, default=Path("."), help="repository root the report was made in")
    parser.add_argument("--exclude", action="append", default=[],
                        help="glob of files to skip, such as a digest file a postUpgradeTask regenerates; repeatable")
    parser.add_argument("--include-tests", action="store_true",
                        help="also scan tests, test, testdata and fixtures directories, which are skipped by default")
    parser.add_argument("--json", action="store_true", help="print findings as JSON")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if not root.is_dir():
        print(f"not a directory: {args.root}", file=sys.stderr)
        return EXIT_USAGE
    try:
        coverage, findings = load_coverage(args.report)
    except (OSError, ValueError) as error:
        print(f"cannot read report {args.report}: {error}", file=sys.stderr)
        return EXIT_USAGE
    findings = deduplicated(findings + scan(root, coverage, args.exclude, {args.report.resolve()}, args.include_tests))
    if args.json:
        print(json.dumps({"findings": [asdict(f) for f in findings]}, indent=2))
    else:
        for finding in findings:
            location = f"{finding.path}:{finding.line}" if finding.line else finding.path
            print(f"{finding.severity}\t{finding.rule}\t{location}\t{finding.message}")
        extracted = sum(len(deps) for deps in coverage.by_file.values())
        print(f"{len(findings)} findings; Renovate extracted {extracted} dependencies from "
              f"{len(coverage.by_file)} files", file=sys.stderr)
        if coverage.needs_token:
            print(f"{coverage.needs_token} dependencies were not looked up for lack of a GitHub token; "
                  "set GITHUB_COM_TOKEN and rerun to check them", file=sys.stderr)
    return EXIT_FINDINGS if findings else EXIT_CLEAN


if __name__ == "__main__":
    sys.exit(main())
