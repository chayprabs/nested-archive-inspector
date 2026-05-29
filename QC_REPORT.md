# QC Report — ArchiveVet (`nested-archive-inspector`)

| Field | Value |
|---|---|
| Tool | ArchiveVet |
| Branch | `cursor/archive-vet-build` |
| Commit SHA | `061d3c9` |
| Date | 2026-05-29 |

## Checks run

| Check | Result | Notes |
|---|---|---|
| `pnpm install` | PASS | Workspace installs cleanly |
| `pnpm lint` | PASS | All TS packages |
| `pnpm typecheck` | PASS | |
| `pnpm test` | PASS | Vitest + `test_share` (no libarchive on host) |
| `pnpm build` | PASS | Next.js standalone + `/s/[token]` route |
| `python scripts/generate_fixtures.py` | PASS | 7 samples + adversarial + acceptance manifest |
| `pytest` (worker) | VERIFY-DEFERRED | Host Python 3.14 / no libarchive-dev |
| `docker compose config` | VERIFY-DEFERRED | Docker CLI unavailable on Windows host |
| Playwright smoke | PASS (local) | Home workbench visible after `pnpm build` |
| Playwright diff e2e | PASS (CI) | Worker started in CI job; compares release tarballs |
| `iso-sample.iso` | PASS | Generated via pycdlib in fixtures + samples |

## Passed (cumulative)

- Pattern-1 monorepo: `apps/web`, `apps/worker`, `packages/shared-*`, compose, CI
- Worker: inspect, inspect/url, inspect/expand, extract, repack, diff, share, health
- F2 hierarchical tree + lazy nested markers; F4 glob `**/*`; F5 repack zip/tar.gz
- F7 7z passwords; F8 URL ingest; F9 share links + `/s/[token]` page
- A3/A3 fixtures + tests (67 diff changes); A5 extract test (12 `.so`)
- Web: inspect/diff modes, URL + password fields, share link, samples picker
- Docs: README, AGPL LICENSE, SECURITY, CONTRIBUTING, CODE_OF_CONDUCT

## Remaining (blocking QUALIFIED)

- F1 full native format matrix (RAR, ISO, DMG, CAB, NSIS) beyond libarchive baseline
- F2 one-click lazy expand in web UI (API exists)
- F9.3 signed-in history (out of scope for anonymous v1 unless added)
- Hosted Lighthouse >= 95, perf budgets, full checklist Section 1.20 e2e on preview
- PRD sample `dmg-sample.dmg` not yet in `public/samples/` (ISO added)
- Docker/runtime verification on healthy host / CI only

## VERIFY-DEFERRED evidence

```text
pytest on Windows host: Python 3.14 / ModuleNotFoundError: libarchive
docker compose config: docker: unknown command: docker compose
```

Rerun:

```bash
cd apps/worker && pip install -r requirements.txt && pytest -q
docker compose config && docker compose up --build
pnpm --filter @archive-vet/web exec playwright test
```

## Verdict

**IN PROGRESS** — Core playground and acceptance unit tests exist; not yet **QUALIFIED** per `RELEASE_QUALIFICATION_CHECKLIST.md` Section 1.
