# Building links from a git remote

Read the remote with `git remote get-url origin` and turn it into a web base URL.

## Remote to web base

| Remote form | Web base |
| --- | --- |
| `https://host/owner/repo.git` | `https://host/owner/repo` |
| `git@host:owner/repo.git` | `https://host/owner/repo` |
| `ssh://git@host[:port]/owner/repo.git` | `https://host/owner/repo` |

Drop the `.git` suffix, the user and the port. Some self-hosted forges serve SSH from a separate host, such as `git-ssh.example.com` beside `git.example.com`; take the web host from the repository's `## Session TL;DR` contract block, or from a URL a tool printed this session (a push often prints the pull request URL). Never guess it.

## Paths on each forge

| Thing | GitHub | GitLab | Forgejo / Gitea | Bitbucket |
| --- | --- | --- | --- | --- |
| Pull request | `/pull/N` | `/-/merge_requests/N` | `/pulls/N` | `/pull-requests/N` |
| Commit | `/commit/SHA` | `/-/commit/SHA` | `/commit/SHA` | `/commits/SHA` |
| Branch | `/tree/BRANCH` | `/-/tree/BRANCH` | `/src/branch/BRANCH` | `/src/BRANCH` |
| Release | `/releases/tag/TAG` | `/-/releases/TAG` | `/releases/tag/TAG` | none |
| File at a branch | `/blob/BRANCH/PATH` | `/-/blob/BRANCH/PATH` | `/src/branch/BRANCH/PATH` | `/src/BRANCH/PATH` |

Tell the forge apart by host (`github.com`, `gitlab.com`, `bitbucket.org`) or, when self-hosted, by the URL a tool printed or the contract block. A submodule has its own remote; build its links from that, not from the parent repository.

## Files in the workspace

Inside the editor or terminal, link a file with a markdown link whose target is its path relative to the workspace root, with `#L42` appended for a line, so it opens locally. Link the forge URL instead when the file only exists on another branch or in a repository that is not checked out here.
