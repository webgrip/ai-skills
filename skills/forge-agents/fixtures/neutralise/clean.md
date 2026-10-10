The export job fails on the third retry with a timeout.

Steps: run the nightly export, wait for the retry, read the job log.
Contact: ops@example.com. The prefix fixtures live in tests/fixtures/export.
Implementation notes and the issue tracker link are in the runbook.

```sh
/usr/local/bin/export --dry-run
echo "@channel closes #4"
```
