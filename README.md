# ArchiveVet (`nested-archive-inspector`)

Open and safely extract ZIP, 7z, RAR, TAR, ISO, DMG and nested archives online — with zip-bomb, path-traversal and symlink protection.

ArchiveVet is a self-hostable Pattern-1 playground: a Next.js web UI talks to a sandboxed Python worker backed by libarchive, 7z, and related native tools.

## Quick start

```bash
pnpm install
python scripts/generate_fixtures.py
docker compose up --build
```

- Web: http://localhost:3000
- Worker health: http://localhost:8000/health

For local development without Docker:

```bash
cd apps/worker && pip install -r requirements.txt && uvicorn src.main:app --reload
pnpm --filter @archive-vet/web dev
```

Set `ARCHIVEVET_WORKER_URL=http://127.0.0.1:8000` for the web app.

## License

AGPL-3.0 — see [LICENSE](LICENSE).
