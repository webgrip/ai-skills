# Repeat loops, random order and break-checks

## Repeat a test

`scripts/repeat_run.py` is the default: per-run timeout that kills the whole process group, parallel
runs, a pass/fail/timeout/missing tally, logs kept only for runs that did not pass, and the machine's
load before and after.

```bash
python3 scripts/repeat_run.py -n 30 -j 6 --timeout 120 --require 'tests 39\b' -- node --test test/upload.test.mjs
python3 scripts/repeat_run.py -n 25 --timeout 300 -- php artisan test --compact --filter=CurrencyConversionTest
python3 scripts/repeat_run.py -n 40 -j 4 -- sh -c 'TEST_DATABASE=app_test_$REPEAT_RUN_INDEX pytest -q tests/test_export.py'
```

- `-j` above 1 only when runs cannot share state: name databases, ports and temp dirs after `REPEAT_RUN_INDEX`, and let the command create or reset what it names.
- `--require` takes the line that proves the whole file ran. Summary lines per runner:

| Runner | Passing summary to require |
| --- | --- |
| node:test (spec reporter) | `ℹ tests 39` and `ℹ fail 0` (grep `ℹ (tests\|pass\|fail\|cancelled)`, not `# tests`) |
| PHPUnit | `OK (39 tests` |
| Pest | `Tests:\s+39 passed` |
| pytest | `39 passed` |
| Jest | `Tests:\s+39 passed, 39 total` |
| Go (`-v`) | count `--- PASS` lines instead |

Runner-native repeats where they exist, each with an explicit timeout:

```bash
go test ./pkg/relay -run 'TestStoppedProcessStaysStopped$' -count=500 -timeout 30m -v 2>&1 | grep -E '^--- (PASS|FAIL)' | sort | uniq -c
go test ./pkg/relay -run 'TestStoppedProcessStaysStopped$' -count=200 -race -cpu 1 -timeout 30m
node --test --test-timeout=120000 test/upload.test.mjs
```

- Go's default `-timeout` is 10 minutes for the whole binary, which a long `-count` loop exceeds.
- node:test has no per-test timeout unless `--test-timeout` is given.
- A runner without a repeat flag gets a shell loop or `repeat_run.py`; count the test command's exit, never a pipe's.

## Expose order dependence

Run in random order, keep the seed from a red run, replay it until the fix holds.

| Runner | Randomise | Replay |
| --- | --- | --- |
| Go | `-shuffle=on` (prints its seed) | `-shuffle=N` |
| PHPUnit | `--order-by random` | `--random-order-seed N` |
| Jest | `--randomize` (within a file) | `--seed N` |
| pytest + pytest-randomly | on when installed | `--randomly-seed N`, or `last` |
| node:test 24.16+ (early development) | `--test-randomize` | `--test-random-seed N` |

A test that fails only after a particular neighbour shares state with it: a row, a cache entry, a
singleton, a file or an environment variable.

## Break-checks

The fix is proven only when undoing it turns the test red.

```bash
git stash push -q -- app/Actions/ConvertCurrency.php && vendor/bin/pest --compact --filter=CurrencyConversion; git stash pop -q
cp scripts/lint.py "$TMPDIR/new.py"; git show HEAD:scripts/lint.py > scripts/lint.py; bash test.sh; cp "$TMPDIR/new.py" scripts/lint.py
git show origin/main:test/actions.test.ts > test/zz-before.test.ts
```

- **Mutation**: change the guarded behaviour by one step (`$lines[$index + 1]`, `<` for `<=`, drop the `await`) and run the test; it must fail with a message that names the behaviour.
- **Before and after**: run the loop against the old copy and the new copy side by side; the old one must fail some runs, the new one none.
- **A weak test shows up here**: a test that stays green with the behaviour broken was asserting a fallback.

## Probe a new CI check

```bash
git commit -q --no-verify -am "test: probe the new check (to be dropped)" && git push -q
git reset -q --hard HEAD~1 && git push -q --force-with-lease
```

Break only the property under check (valid code with bad formatting, not code that fails to build), so
the jobs before it pass and the new job is the one that fails. Do this on your own branch only.

## node:test traps

- `t.after` hooks run first in, first out. Registering "delete the data directory" before "close the server" deletes the directory mid-write (`ENOTEMPTY`).
- `--test-force-exit` ends the process once known tests finish; a run has reported fewer tests than the file holds while passing. Require the count, or drop the flag.
- Faking a timer API globally (every `setTimeout`) also fakes the timers the runner and libraries rely on, and has hung runs; inject or stub only the one timer the code under test uses.
