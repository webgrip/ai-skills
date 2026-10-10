#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

EXIT_FOUND = 0
EXIT_ABSENT = 1
EXIT_ERROR = 2
EXIT_PIN_DIFFERS = 3

MANIFEST_MEDIA_TYPES = (
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.v2+json",
)
INDEX_MEDIA_TYPES = MANIFEST_MEDIA_TYPES[:2]
DOCKER_HUB_NAMES = {"docker.io", "index.docker.io", "registry-1.docker.io"}
DOCKER_HUB_API_HOST = "registry-1.docker.io"
PLAIN_HTTP_HOSTS = {"localhost", "127.0.0.1"}
DIGEST_PATTERN = re.compile(r"^sha256:[a-f0-9]{64}$")
CHALLENGE_PARAM = re.compile(r'(\w+)="([^"]*)"')


class RegistryError(Exception):
    pass


@dataclass(frozen=True)
class ImageReference:
    registry: str
    repository: str
    tag: Optional[str]
    digest: Optional[str]

    @property
    def manifest_reference(self) -> str:
        return self.tag or self.digest or "latest"

    @property
    def label(self) -> str:
        separator = "@" if self.manifest_reference == self.digest else ":"
        return f"{self.registry}/{self.repository}{separator}{self.manifest_reference}"


@dataclass(frozen=True)
class ManifestHead:
    digest: str
    media_type: str


def parse_image_reference(text: str) -> ImageReference:
    remainder, _, digest = text.strip().partition("@")
    if digest and not DIGEST_PATTERN.match(digest):
        raise RegistryError(f"not a sha256 digest: {digest}")
    first, slash, rest = remainder.partition("/")
    has_registry = bool(slash) and ("." in first or ":" in first or first == "localhost")
    registry = first if has_registry else "docker.io"
    path = rest if has_registry else remainder
    name, colon, tag = path.rpartition(":")
    if not colon or "/" in tag:
        name, tag = path, ""
    if not name:
        raise RegistryError(f"no repository in {text!r}")
    if registry in DOCKER_HUB_NAMES:
        registry = DOCKER_HUB_API_HOST
        if "/" not in name:
            name = f"library/{name}"
    return ImageReference(registry, name, tag or None, digest or None)


def registry_base_url(registry: str) -> str:
    host = registry.split(":")[0]
    scheme = "http" if host in PLAIN_HTTP_HOSTS else "https"
    return f"{scheme}://{registry}"


def parse_bearer_challenge(header: str) -> Dict[str, str]:
    scheme, _, params = header.strip().partition(" ")
    if scheme.lower() != "bearer":
        raise RegistryError(f"registry wants {scheme or 'unknown'} auth; anonymous pull is not allowed")
    return dict(CHALLENGE_PARAM.findall(params))


def fetch_anonymous_token(challenge: Dict[str, str], repository: str, timeout: float) -> str:
    realm = challenge.get("realm")
    if not realm:
        raise RegistryError("bearer challenge has no realm")
    query = {"scope": challenge.get("scope") or f"repository:{repository}:pull"}
    if challenge.get("service"):
        query["service"] = challenge["service"]
    url = f"{realm}?{urllib.parse.urlencode(query)}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body = json.load(response)
    except (urllib.error.URLError, ValueError) as error:
        raise RegistryError(f"token request to {realm} failed: {error}") from error
    token = body.get("token") or body.get("access_token")
    if not token:
        raise RegistryError(f"token endpoint {realm} returned no token")
    return token


def manifest_request(url: str, method: str, token: Optional[str]) -> urllib.request.Request:
    headers = {"Accept": ", ".join(MANIFEST_MEDIA_TYPES)}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(url, method=method, headers=headers)


def open_manifest(url: str, method: str, token: Optional[str], timeout: float):
    return urllib.request.urlopen(manifest_request(url, method, token), timeout=timeout)


def head_manifest(reference: ImageReference, timeout: float) -> Optional[ManifestHead]:
    url = f"{registry_base_url(reference.registry)}/v2/{reference.repository}/manifests/{reference.manifest_reference}"
    token = None
    for attempt in range(2):
        try:
            with open_manifest(url, "HEAD", token, timeout) as response:
                return manifest_head_from(response, url, token, timeout)
        except urllib.error.HTTPError as error:
            status, challenge_header = error.code, error.headers.get("WWW-Authenticate", "")
            error.close()
            if status == 404:
                return None
            if status == 401 and attempt == 0:
                token = fetch_anonymous_token(parse_bearer_challenge(challenge_header), reference.repository, timeout)
                continue
            raise RegistryError(f"{url} answered HTTP {status}") from None
        except urllib.error.URLError as error:
            raise RegistryError(f"cannot reach {url}: {error.reason}") from error
    raise RegistryError(f"{url} still refused the anonymous token")


def manifest_head_from(response, url: str, token: Optional[str], timeout: float) -> ManifestHead:
    media_type = response.headers.get("Content-Type", "").split(";")[0].strip()
    digest = response.headers.get("Docker-Content-Digest", "").strip()
    if not digest:
        with open_manifest(url, "GET", token, timeout) as body_response:
            digest = "sha256:" + hashlib.sha256(body_response.read()).hexdigest()
    return ManifestHead(digest, media_type)


def describe(head: ManifestHead) -> str:
    kind = "multi-arch index" if head.media_type in INDEX_MEDIA_TYPES else "single manifest"
    return f"{head.digest}\t{head.media_type}\t{kind}"


def check(reference_text: str, timeout: float) -> Tuple[int, str]:
    reference = parse_image_reference(reference_text)
    head = head_manifest(ImageReference(reference.registry, reference.repository, reference.tag, None)
                         if reference.tag else reference, timeout)
    if head is None:
        return EXIT_ABSENT, f"absent\t{reference.label}"
    if reference.tag and reference.digest and head.digest != reference.digest:
        return EXIT_PIN_DIFFERS, f"{describe(head)}\tpinned {reference.digest} differs"
    return EXIT_FOUND, describe(head)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Read an image's manifest digest from its registry without credentials. "
        "Exit 0: published (digest printed); 1: tag absent; 2: error; 3: tag exists but the pinned digest differs.")
    parser.add_argument("images", nargs="+", help="image references such as nginx:1.27, ghcr.io/owner/app:v1.2.3, "
                        "or repo:tag@sha256:... to compare a pin with what the tag points at now")
    parser.add_argument("--timeout", type=float, default=20.0, help="seconds per HTTP request (default 20)")
    args = parser.parse_args(argv)
    worst = EXIT_FOUND
    for image in args.images:
        try:
            code, line = check(image, args.timeout)
        except RegistryError as error:
            code, line = EXIT_ERROR, f"error\t{error}"
        print(f"{image}\t{line}")
        worst = max(worst, code)
    return worst


if __name__ == "__main__":
    sys.exit(main())
