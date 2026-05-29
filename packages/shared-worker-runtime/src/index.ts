export function resolveWorkerBaseUrl(
  env: Record<string, string | undefined> = typeof process !== "undefined" ? process.env : {}
): string {
  return (
    env.ARCHIVEVET_WORKER_URL ||
    env.NEXT_PUBLIC_ARCHIVEVET_WORKER_URL ||
    "http://127.0.0.1:8000"
  ).replace(/\/$/, "");
}
