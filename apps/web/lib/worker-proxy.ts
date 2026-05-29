import { resolveWorkerBaseUrl } from "@archive-vet/shared-worker-runtime";

export function resolveWorkerOrigin(): string {
  return resolveWorkerBaseUrl(process.env);
}

export function resolvePublicOrigin(
  requestOrigin: string,
  forwardedProto?: string | null,
  forwardedHost?: string | null,
  host?: string | null
): string {
  const proto = forwardedProto || "http";
  const resolvedHost = forwardedHost || host || new URL(requestOrigin).host;
  return `${proto}://${resolvedHost}`;
}

export function rewriteWorkerPayload<T>(payload: T): T {
  return payload;
}
