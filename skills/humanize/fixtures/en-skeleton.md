## Introduction

Secrets management in Kubernetes is a topic that comes up in every platform team. This short guide covers the approach we settled on after trying three different tools over two years. It is opinionated, and it is what we run today.

### Why a vault at all

A vault is a single place that holds every credential, with an audit log of who read what and when. Without one, credentials end up in environment variables, in CI settings pages, and occasionally in a commit somebody made at eleven at night. We have all done it.

### What it costs you

Running one is not free. Somebody has to unseal it after a restart, rotate the root token, and explain to the new hire why the deploy failed at nine on a Monday because a lease expired over the weekend. Budget a day a month for it, and more in the first quarter.

## Conclusion

The vault is the boring part, and boring is the point.
