#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Dict, Iterator, List, Optional

ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\x1b\][^\x07]*\x07")
GITLAB_SECTION_MARKER = re.compile(r"section_(?:start|end):\d+:[^\r\n]*?\r")
GITHUB_LOG_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z ")
IMAGE_DIGEST_PATTERNS = (
    re.compile(r"Using docker image \S+ for \S+ with digest (\S+@sha256:[0-9a-f]{64})"),
    re.compile(r"Digest: (sha256:[0-9a-f]{64})"),
)
MERGE_REQUEST_REF = re.compile(r"^refs/merge-requests/(\d+)/")
NEXT_LINK = re.compile(r'<([^>]+)>\s*;\s*rel="next"')
SECRET_HEADERS = {"authorization", "private-token"}
FAILED_GITHUB_CONCLUSIONS = {"failure", "timed_out"}
MISSING_LOG_STATUSES = {404, 410}
EXCERPT_LIMIT = 240
PAGE_SIZE = 100
REQUEST_TIMEOUT_SECONDS = 60


class ForgeError(Exception):
    pass


@dataclass
class Response:
    status: int
    headers: Dict[str, str]
    body: bytes


Transport = Callable[[str, Dict[str, str]], Response]


@dataclass
class FailedJob:
    job_id: int
    name: str
    pipeline_id: int
    change: str
    ref: str
    sha: str
    created_at: str
    url: str
    allow_failure: bool = False
    attempt: int = 1
    attempts: int = 1


@dataclass
class Match:
    job: FailedJob
    excerpt: str
    image_digest: str


@dataclass
class Criteria:
    job_pattern: re.Pattern
    text_pattern: re.Pattern
    since: Optional[datetime.datetime]
    limit: int


@dataclass
class Report:
    forge: str
    job_pattern: str
    text: str
    listed: int = 0
    scanned: int = 0
    unavailable: List[int] = field(default_factory=list)
    matches: List[Match] = field(default_factory=list)


def build_request(url: str, headers: Dict[str, str]) -> urllib.request.Request:
    request = urllib.request.Request(url, method="GET")
    for name, value in headers.items():
        if name.lower() in SECRET_HEADERS:
            request.add_unredirected_header(name, value)
        else:
            request.add_header(name, value)
    return request


def urllib_transport(url: str, headers: Dict[str, str]) -> Response:
    try:
        with urllib.request.urlopen(build_request(url, headers), timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return Response(response.status, lower_keys(response.headers.items()), response.read())
    except urllib.error.HTTPError as error:
        return Response(error.code, lower_keys(error.headers.items()), error.read())
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        reason = getattr(error, "reason", error)
        raise ForgeError(f"cannot reach {urllib.parse.urlsplit(url).netloc}: {reason}") from error


def lower_keys(items) -> Dict[str, str]:
    return {name.lower(): value for name, value in items}


def parse_time(value: str) -> datetime.datetime:
    normalised = value.strip().replace("Z", "+00:00")
    if re.search(r"\.\d+", normalised):
        normalised = re.sub(r"\.(\d+)", lambda digits: "." + digits.group(1)[:6].ljust(6, "0"), normalised)
    parsed = datetime.datetime.fromisoformat(normalised)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed.astimezone(datetime.timezone.utc)


def parse_day(value: str) -> datetime.datetime:
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"expected YYYY-MM-DD, got {value!r}") from error


def positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"expected a whole number, got {value!r}") from error
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def clean_lines(text: str) -> List[str]:
    without_markers = GITLAB_SECTION_MARKER.sub("", ANSI_ESCAPE.sub("", text))
    lines = []
    for raw in without_markers.split("\n"):
        visible = raw.rstrip("\r").split("\r")[-1]
        lines.append(GITHUB_LOG_TIMESTAMP.sub("", visible))
    return lines


def first_match(lines: List[str], pattern: re.Pattern) -> Optional[str]:
    for line in lines:
        if pattern.search(line):
            excerpt = line.strip()
            return excerpt if len(excerpt) <= EXCERPT_LIMIT else excerpt[: EXCERPT_LIMIT - 1] + "…"
    return None


def image_digest(lines: List[str]) -> str:
    for line in lines:
        for pattern in IMAGE_DIGEST_PATTERNS:
            found = pattern.search(line)
            if found:
                return found.group(1)
    return ""


class Client:
    def __init__(self, base_url: str, headers: Dict[str, str], transport: Transport, token_hint: str):
        self.base_url = base_url.rstrip("/")
        self.headers = headers
        self.transport = transport
        self.token_hint = token_hint

    def get(self, url: str) -> Response:
        response = self.transport(url, self.headers)
        if response.status == 200:
            return response
        raise ForgeError(self.describe_failure(response, url))

    def get_log(self, url: str) -> Optional[str]:
        response = self.transport(url, self.headers)
        if response.status in MISSING_LOG_STATUSES:
            return None
        if response.status != 200:
            raise ForgeError(self.describe_failure(response, url))
        return response.body.decode("utf-8", errors="replace")

    def pages(self, url: str) -> Iterator[object]:
        next_url: Optional[str] = url
        while next_url:
            response = self.get(next_url)
            try:
                yield json.loads(response.body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise ForgeError(f"{urllib.parse.urlsplit(next_url).path} did not return JSON: {error}") from error
            link = NEXT_LINK.search(response.headers.get("link", ""))
            next_url = link.group(1) if link else None

    def describe_failure(self, response: Response, url: str) -> str:
        path = urllib.parse.urlsplit(url).path
        rate_limited = response.status == 429 or response.headers.get("x-ratelimit-remaining") == "0"
        if rate_limited:
            return f"rate limited on {path}; wait for the reset or lower --limit"
        if response.status in (401, 403):
            return f"{response.status} on {path}; {self.token_hint}"
        if response.status == 404:
            return f"404 on {path}; check the project path, or the token cannot see it ({self.token_hint})"
        return f"{response.status} on {path}"


class GitLab:
    name = "gitlab"
    run_noun = "pipelines"
    change_noun = "merge requests"

    def __init__(self, client: Client, project: str):
        self.client = client
        self.project = urllib.parse.quote(project, safe="")
        self.listed = 0

    def failed_jobs(self, criteria: Criteria) -> Iterator[FailedJob]:
        query = urllib.parse.urlencode({"scope[]": "failed", "per_page": PAGE_SIZE})
        for page in self.client.pages(f"{self.client.base_url}/projects/{self.project}/jobs?{query}"):
            for job in page:
                if self.listed >= criteria.limit:
                    return
                if criteria.since and parse_time(job["created_at"]) < criteria.since:
                    return
                self.listed += 1
                if criteria.job_pattern.fullmatch(job["name"]):
                    yield self.to_failed_job(job)

    def to_failed_job(self, job: dict) -> FailedJob:
        pipeline = job.get("pipeline") or {}
        ref = pipeline.get("ref") or job.get("ref") or ""
        merge_request = MERGE_REQUEST_REF.match(ref)
        return FailedJob(
            job_id=job["id"],
            name=job["name"],
            pipeline_id=pipeline.get("id", 0),
            change=f"!{merge_request.group(1)}" if merge_request else "",
            ref=ref,
            sha=pipeline.get("sha") or (job.get("commit") or {}).get("id", ""),
            created_at=job["created_at"],
            url=job.get("web_url", ""),
            allow_failure=bool(job.get("allow_failure")),
        )

    def log(self, job: FailedJob) -> Optional[str]:
        return self.client.get_log(f"{self.client.base_url}/projects/{self.project}/jobs/{job.job_id}/trace")


class GitHub:
    name = "github"
    run_noun = "runs"
    change_noun = "pull requests"

    def __init__(self, client: Client, repo: str, workflow: Optional[str]):
        self.client = client
        self.repo = repo.strip("/")
        self.workflow = workflow.rsplit("/", 1)[-1] if workflow else None
        self.listed = 0

    def runs_url(self, criteria: Criteria) -> str:
        parameters = {"status": "completed", "per_page": PAGE_SIZE}
        if criteria.since:
            parameters["created"] = f">={criteria.since.date().isoformat()}"
        scope = f"/actions/workflows/{urllib.parse.quote(self.workflow, safe='')}" if self.workflow else "/actions"
        return f"{self.client.base_url}/repos/{self.repo}{scope}/runs?{urllib.parse.urlencode(parameters)}"

    def failed_jobs(self, criteria: Criteria) -> Iterator[FailedJob]:
        for page in self.client.pages(self.runs_url(criteria)):
            for run in page.get("workflow_runs", []):
                if self.listed >= criteria.limit:
                    return
                self.listed += 1
                yield from self.failed_jobs_of_run(run, criteria)

    def failed_jobs_of_run(self, run: dict, criteria: Criteria) -> Iterator[FailedJob]:
        jobs_url = f"{self.client.base_url}/repos/{self.repo}/actions/runs/{run['id']}/jobs?filter=all&per_page={PAGE_SIZE}"
        pull_requests = [f"#{pull['number']}" for pull in run.get("pull_requests") or []]
        for page in self.client.pages(jobs_url):
            for job in page.get("jobs", []):
                if job.get("conclusion") not in FAILED_GITHUB_CONCLUSIONS:
                    continue
                if not criteria.job_pattern.fullmatch(job["name"]):
                    continue
                yield FailedJob(
                    job_id=job["id"],
                    name=job["name"],
                    pipeline_id=run["id"],
                    change=",".join(pull_requests),
                    ref=run.get("head_branch") or "",
                    sha=job.get("head_sha") or run.get("head_sha", ""),
                    created_at=job.get("started_at") or run["created_at"],
                    url=job.get("html_url", ""),
                    attempt=job.get("run_attempt") or 1,
                    attempts=run.get("run_attempt") or 1,
                )

    def log(self, job: FailedJob) -> Optional[str]:
        return self.client.get_log(f"{self.client.base_url}/repos/{self.repo}/actions/jobs/{job.job_id}/logs")


class LogCache:
    def __init__(self, directory: Optional[Path]):
        self.directory = directory
        if directory:
            directory.mkdir(parents=True, exist_ok=True)

    def path(self, forge: str, job_id: int) -> Optional[Path]:
        return self.directory / f"{forge}-{job_id}.log" if self.directory else None

    def fetch(self, forge, job: FailedJob) -> Optional[str]:
        cached = self.path(forge.name, job.job_id)
        if cached and cached.exists():
            return cached.read_text(encoding="utf-8", errors="replace")
        text = forge.log(job)
        if cached and text is not None:
            cached.write_text(text, encoding="utf-8")
        return text


def scan(forge, criteria: Criteria, cache: LogCache, text: str) -> Report:
    report = Report(forge=forge.name, job_pattern=criteria.job_pattern.pattern, text=text)
    for job in forge.failed_jobs(criteria):
        report.scanned += 1
        log_text = cache.fetch(forge, job)
        if log_text is None:
            report.unavailable.append(job.job_id)
            continue
        lines = clean_lines(log_text)
        excerpt = first_match(lines, criteria.text_pattern)
        if excerpt is not None:
            report.matches.append(Match(job, excerpt, image_digest(lines)))
    report.listed = forge.listed
    return report


def summarise(report: Report, forge) -> Dict[str, object]:
    jobs = [match.job for match in report.matches]
    changes = sorted({change for job in jobs for change in job.change.split(",") if change}, key=change_order)
    branches: Dict[str, int] = {}
    for job in jobs:
        if not job.change:
            branches[job.ref] = branches.get(job.ref, 0) + 1
    days = sorted(parse_time(job.created_at).date().isoformat() for job in jobs)
    digests = sorted({match.image_digest for match in report.matches if match.image_digest})
    return {
        "failures": len(jobs),
        forge.run_noun: len({job.pipeline_id for job in jobs}),
        forge.change_noun: changes,
        "branches": branches,
        "first": days[0] if days else None,
        "last": days[-1] if days else None,
        "image_digests": digests,
        "matches_without_digest": sum(1 for match in report.matches if not match.image_digest),
    }


def change_order(change: str):
    digits = re.sub(r"\D", "", change)
    return (change[:1], int(digits) if digits else 0)


def render_text(report: Report, forge, out) -> None:
    for match in report.matches:
        job = match.job
        where = job.change or job.ref or "?"
        flags = []
        if job.allow_failure:
            flags.append("allow_failure")
        if job.attempts > 1:
            flags.append(f"attempt {job.attempt}/{job.attempts}")
        digest = short_digest(match.image_digest)
        parts = [
            parse_time(job.created_at).date().isoformat(),
            f"{where:<8}",
            f"{forge.run_noun[:-1]} {job.pipeline_id}",
            f"job {job.job_id}",
            job.sha[:8],
        ] + flags + ([f"image {digest}"] if digest else []) + [job.url]
        print("  ".join(part for part in parts if part), file=out)
        print(f"    {match.excerpt}", file=out)
    summary = summarise(report, forge)
    print("", file=out)
    print(
        f"{len(report.matches)} of {report.scanned} failed '{report.job_pattern}' jobs contain the text"
        f" ({report.listed} {'failed jobs' if forge.name == 'gitlab' else 'completed runs'} listed;"
        f" logs unavailable: {len(report.unavailable)})",
        file=out,
    )
    if not report.matches:
        return
    branch_text = ", ".join(f"{name} ({count})" for name, count in sorted(summary["branches"].items())) or "none"
    print(
        f"spread: {summary[forge.run_noun]} {forge.run_noun}, {len(summary[forge.change_noun])} {forge.change_noun}"
        f" ({', '.join(summary[forge.change_noun]) or 'none'}), branch {forge.run_noun}: {branch_text}",
        file=out,
    )
    print(f"first {summary['first']}, last {summary['last']}", file=out)
    digests = summary["image_digests"]
    unknown = summary["matches_without_digest"]
    digest_text = f"{len(digests)} distinct ({', '.join(short_digest(d) for d in digests)})" if digests else "none in the logs"
    print(f"image digests: {digest_text}" + (f"; {unknown} matching logs print none" if digests and unknown else ""), file=out)


def short_digest(digest: str) -> str:
    if not digest:
        return ""
    head, _, hex_part = digest.rpartition("sha256:")
    return f"{head}sha256:{hex_part[:12]}"


def render_json(report: Report, forge, out) -> None:
    payload = asdict(report)
    payload["summary"] = summarise(report, forge)
    json.dump(payload, out, indent=2)
    print("", file=out)


def compile_pattern(value: str, as_regex: bool, flag: str) -> re.Pattern:
    try:
        return re.compile(value if as_regex else re.escape(value))
    except re.error as error:
        raise ForgeError(f"{flag} is not a valid regular expression: {error}") from error


def parse_arguments(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Count how often one test or assertion failed across CI pipelines and merge requests "
        "(read-only GitLab or GitHub API calls).",
    )
    forges = parser.add_subparsers(dest="forge", required=True)

    gitlab = forges.add_parser("gitlab", help="GitLab project; token from GITLAB_TOKEN (read_api)")
    gitlab.add_argument("--project", required=True, help="group/subgroup/project or numeric id")
    gitlab.add_argument("--api-url", default=os.environ.get("CI_API_V4_URL", "https://gitlab.com/api/v4"))

    github = forges.add_parser("github", help="GitHub repository; token from GITHUB_TOKEN or GH_TOKEN")
    github.add_argument("--repo", required=True, help="owner/name")
    github.add_argument("--workflow", help="workflow file such as ci.yml or .github/workflows/ci.yml, to list only its runs")
    github.add_argument("--api-url", default=os.environ.get("GITHUB_API_URL", "https://api.github.com"))

    for sub in (gitlab, github):
        sub.add_argument("--job", required=True, help="job name, as a regular expression matched in full")
        sub.add_argument("--grep", required=True, help="text the failing log must contain (literal)")
        sub.add_argument("--regex", action="store_true", help="treat --grep as a regular expression")
        sub.add_argument("--since", type=parse_day, help="only jobs created on or after YYYY-MM-DD")
        sub.add_argument("--limit", type=positive_int, default=300, help="most recent records to list (default 300)")
        sub.add_argument("--log-dir", type=Path, help="keep downloaded logs here and reuse them on later runs")
        sub.add_argument("--json", action="store_true", help="print JSON instead of text")
    return parser.parse_args(argv)


def build_forge(arguments: argparse.Namespace, environment: Dict[str, str], transport: Transport):
    if arguments.forge == "gitlab":
        token = environment.get("GITLAB_TOKEN", "")
        headers = {"PRIVATE-TOKEN": token} if token else {}
        client = Client(arguments.api_url, headers, transport, "set GITLAB_TOKEN to a token with read_api")
        return GitLab(client, arguments.project)
    token = environment.get("GITHUB_TOKEN") or environment.get("GH_TOKEN", "")
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    client = Client(arguments.api_url, headers, transport, "set GITHUB_TOKEN or GH_TOKEN; job logs need a token with actions read access")
    return GitHub(client, arguments.repo, arguments.workflow)


def main(argv: Optional[List[str]] = None, transport: Transport = urllib_transport,
         environment: Optional[Dict[str, str]] = None, out=sys.stdout, err=sys.stderr) -> int:
    arguments = parse_arguments(sys.argv[1:] if argv is None else argv)
    environment = dict(os.environ) if environment is None else environment
    try:
        criteria = Criteria(
            job_pattern=compile_pattern(arguments.job, True, "--job"),
            text_pattern=compile_pattern(arguments.grep, arguments.regex, "--grep"),
            since=arguments.since,
            limit=arguments.limit,
        )
        forge = build_forge(arguments, environment, transport)
        report = scan(forge, criteria, LogCache(arguments.log_dir), arguments.grep)
    except ForgeError as error:
        print(f"ci_recurrence: {error}", file=err)
        return 2
    except (KeyError, TypeError) as error:
        print(f"ci_recurrence: unexpected API response shape ({type(error).__name__}: {error})", file=err)
        return 2
    (render_json if arguments.json else render_text)(report, forge, out)
    return 0 if report.matches else 1


if __name__ == "__main__":
    sys.exit(main())
