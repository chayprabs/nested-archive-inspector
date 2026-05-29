# QC Report — ArchiveVet (`nested-archive-inspector`)

| Field | Value |
|---|---|
| Tool | ArchiveVet |
| Branch | `cursor/archive-vet-build` |
| Commit SHA | `e1da64a` |
| Date | 2026-05-29 |

## Checks run

| Check | Result | Notes |
|---|---|---|
| `pnpm install` | PASS | Workspace installs cleanly |
| `pnpm lint` | PASS | All TS packages |
| `pnpm typecheck` | PASS | |
| `pnpm test` | PASS | Vitest (packages + web passWithNoTests) |
| `pnpm build` | PASS | Next.js standalone build |
| `python scripts/generate_fixtures.py` | PASS | Samples + worker fixtures |
| `pytest` (worker) | VERIFY-DEFERRED | Host Python 3.14; pydantic wheel build fails. CI uses Python 3.12 + `libarchive-dev` |
| `docker compose config` | VERIFY-DEFERRED | Docker CLI unavailable on verifier host (`docker: unknown command: docker compose`) |

## Passed (this iteration)

- Monorepo scaffold: `apps/web`, `apps/worker`, `packages/shared-*`, compose files, CI workflows
- Worker routes: `/health`, `/v1/inspect`, `/v1/extract`, `/v1/diff`
- Core safety flags (path traversal, symlink escape, compression ratio)
- Web playground with FileDrop, SamplePicker, virtualized tree (react-virtuoso)
- AGPL LICENSE, README, SECURITY, CONTRIBUTING, CODE_OF_CONDUCT
- Sample ZIP fixtures under `apps/web/public/samples/`

## Remaining (blocking product completion)

- F1 full format matrix (7z, RAR, ISO, DMG, CAB, NSIS, …) beyond libarchive ZIP/TAR baseline
- F2 nested lazy-expand tree (currently flat libarchive walk)
- F5 repack endpoint
- F7 password-protected archives
- F8 URL ingest, F9 share/history
- PRD acceptance A3 (67 diff changes), A5 (12 `.so` extracts) — fixtures not yet canonical
- Lighthouse >= 95, perf budgets, e2e Playwright
- Hosted deployment verification

## VERIFY-DEFERRED evidence

```text
# Worker pytest (local)
Python 3.14 + pydantic-core build: PyO3 max supported 3.13
ModuleNotFoundError: libarchive (no libarchive-dev on Windows host)

# Docker
docker compose config -> docker: unknown command: docker compose
```

Rerun on CI / healthy host:

```bash
cd apps/worker && pip install -r requirements.txt && pytest -q
docker compose config && docker compose up --build
```

## Verdict

**IN PROGRESS** — Foundation shipped and web build passes; not yet QUALIFIED per `RELEASE_QUALIFICATION_CHECKLIST.md` Section 1.
