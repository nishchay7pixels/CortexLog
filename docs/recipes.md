# CortexLog Recipes

## 1) Daily engineering loop

```bash
python3 cortexlog.py checkpoint --goal "Finish auth hardening" --decision "Use signed nonce" --next "Patch middleware" --next "Add tests"
python3 cortexlog.py add "Middleware patch in progress" --tags security
python3 cortexlog.py trace --claim "Nonce validation blocks replay" --outcome confirmed --evidence "python3 -m unittest discover -s tests -q"
python3 cortexlog.py resolve "Patch middleware"
python3 cortexlog.py handoff --verified --format prompt
```

## 2) Pre-PR gate (manual)

```bash
python3 cortexlog.py verify
```

If non-zero exit code, fix issues before opening the PR.

## 3) CI gate in GitHub Actions

Add a step in `.github/workflows/ci.yml`:

```yaml
- name: Verify TruthGraph
  run: python cortexlog.py verify
```

## 4) Incident timeline capture

```bash
python3 cortexlog.py checkpoint --goal "Stabilize checkout API" --decision "Rollback cache layer" --next "Confirm error rate drop"
python3 cortexlog.py add "Error spike from 2% to 18%" --tags incident,api
python3 cortexlog.py trace --claim "Rollback reduced 5xx errors" --outcome confirmed --evidence "dashboard screenshot id=abc123"
python3 cortexlog.py handoff --verified --format json > incident-handoff.json
```

## 5) Multi-agent baton pass

Agent A:

```bash
python3 cortexlog.py checkpoint --goal "Refactor parser" --decision "Keep tokenizer unchanged" --next "Implement AST normalization"
python3 cortexlog.py handoff --verified --format json > handoff.json
```

Agent B:

```bash
python3 cortexlog.py search "AST normalization"
python3 cortexlog.py list --kind checkpoint
```

## 6) Contradiction correction flow

```bash
python3 cortexlog.py trace --claim "All migrations are reversible" --outcome failed --evidence "rollback test failed"
python3 cortexlog.py trace --claim "All migrations are reversible" --outcome confirmed --evidence "added down migration + test"
python3 cortexlog.py verify
```

## 7) Project metrics snapshot

```bash
python3 cortexlog.py stats
python3 cortexlog.py list --day 2026-02-28
```
