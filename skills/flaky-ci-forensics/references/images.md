# Images: digests, layers and why sizes drift

## Was it the same image?

Compare the digest each job ran, never the tag (tags move) and never the size.

| Where | Line to grep in the job log |
| --- | --- |
| GitLab Runner, docker executor | `Using docker image sha256:... for IMAGE with digest REPO@sha256:...` |
| Any job that runs `docker pull` (GitHub container jobs in "Initialize containers") | `Digest: sha256:...` |
| GitLab Runner, Kubernetes executor | none; pin `image:` by digest, or print it from the job |

`scripts/ci_recurrence.py` prints the digest next to every match. Same digest in a failing and a
passing job: the image is ruled out, look at timing, order and shared state.

## Fetch manifests and layers

Any registry client works: `crane manifest IMAGE`, `crane blob IMAGE@sha256:...`,
`skopeo inspect --raw docker://IMAGE`, `docker buildx imagetools inspect --raw IMAGE`. With plain
curl, the registry token flow:

```bash
R=registry.example.com; P=group/app/testing
curl -sI "https://$R/v2/" | grep -i www-authenticate
TOKEN=$(curl -s -u "$USER:$REGISTRY_TOKEN" "$REALM?service=$SERVICE&scope=repository:$P:pull" | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')
ACCEPT='application/vnd.oci.image.index.v1+json,application/vnd.oci.image.manifest.v1+json,application/vnd.docker.distribution.manifest.list.v2+json,application/vnd.docker.distribution.manifest.v2+json'
curl -s -H "Authorization: Bearer $TOKEN" -H "Accept: $ACCEPT" "https://$R/v2/$P/manifests/$TAG_OR_DIGEST" > a.json
curl -sL -H "Authorization: Bearer $TOKEN" "https://$R/v2/$P/blobs/$LAYER_DIGEST" -o layer.tar.gz
```

- `REALM` and `SERVICE` come from the `www-authenticate` header; on GitLab the realm is `https://gitlab.com/jwt/auth` (self-managed: the instance's `/jwt/auth`) and the service `container_registry`.
- An index (multi-platform) lists one manifest per platform; fetch the one for the runner's platform.
- List layers side by side: `python3 -c 'import json,sys; [print(l["digest"], l["size"]) for l in json.load(open(sys.argv[1]))["layers"]]' a.json`. A layer digest present in both images is byte-identical; only the rest differ.

## Compare content

```bash
python3 scripts/layer_diff.py a/1.tar.gz a/2.tar.gz a/3.tar.gz --against b/1.tar.gz b/2.tar.gz b/3.tar.gz
```

Pass every layer of each image in manifest order (shared layers can be the same file). It flattens
each image, honouring whiteouts (`.wh.NAME`) and opaque directories (`.wh..wh..opq`), and reports:

- per layer, the files it re-adds with content identical to what a lower layer already holds, and which metadata differs;
- for the final trees: added, removed, content changed, mode or owner changed, and the count that differs only in mtime;
- `final trees: equivalent` (exit 0) when only mtimes differ, `different` (exit 1) otherwise, exit 2 on unreadable input.

Python's `tarfile` reads tar, gzip, bzip2 and xz; decompress a zstd layer (`zstd -d`) first. With
one image and no `--against`, it reports only the re-adds.

## Why same-content files land in a layer again

BuildKit computes a layer as the diff between the step's snapshot and its parent:

- The overlay differ treats a file present in both as unchanged only when mode, uid, gid, rdev, `security.capability`, size **and mtime** are equal; it reads contents only when both mtimes have zero nanoseconds and the same seconds ([overlay_linux.go](https://github.com/moby/buildkit/blob/master/util/overlay/overlay_linux.go); the fallback differ in [continuity fs/path.go](https://github.com/containerd/continuity/blob/main/fs/path.go) does the same).
- COPY cache keys come from tarsum headers that exclude mtime ([contenthash/tarsum.go](https://github.com/moby/buildkit/blob/master/cache/contenthash/tarsum.go)), and copies preserve source mtimes ([fsutil copy](https://github.com/tonistiigi/fsutil/blob/master/copy/copy_linux.go)).
- So after a fresh clone, `COPY composer.json composer.lock ./` stays a cache hit carrying the old mtimes, the later `COPY . .` writes the new ones, and every such file is in the last layer again.
- Docker Engine's legacy overlay2 graphdriver tars the whole upper directory, so every file a COPY writes lands in the layer even with identical metadata.
- `COPY --link` copies into an empty directory and never diffs, so its layer always holds every copied file ([reference](https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/reference.md#copy---link)).
- `SOURCE_DATE_EPOCH` and `rewrite-timestamp=true` change timestamps in the image config and tar headers, not which files a layer holds ([build-repro.md](https://github.com/moby/buildkit/blob/master/docs/build-repro.md)).

Consequence: builds of one commit are not byte-reproducible across checkouts and cache states, and
size or digest drift alone says nothing about content.

Mitigations, derived from the source and not measured: keep the late copy disjoint from the early
ones (`COPY --exclude=composer.json --exclude=composer.lock . .`), or make context mtimes deterministic
before the build (helps only on the BuildKit differ path, not on legacy overlay2).
