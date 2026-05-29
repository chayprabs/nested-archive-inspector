import type { DiffResult, InspectResult } from "@archive-vet/shared-types";
import { flattenTree } from "@/lib/flatten-tree";
import { headers } from "next/headers";

export const dynamic = "force-dynamic";

type SharePayload = {
  kind: "inspect" | "diff";
  payload: InspectResult | DiffResult;
  expiresAt: string;
};

export default async function SharedInspectionPage({
  params
}: {
  params: Promise<{ token: string }>;
}) {
  const { token } = await params;
  const headerList = await headers();
  const host = headerList.get("x-forwarded-host") ?? headerList.get("host") ?? "localhost:3000";
  const proto = headerList.get("x-forwarded-proto") ?? "http";
  const response = await fetch(`${proto}://${host}/api/worker/v1/share/${token}`, {
    cache: "no-store"
  });

  if (!response.ok) {
    return (
      <main className="shell">
        <h1>Share link unavailable</h1>
        <p>This inspection may have expired.</p>
      </main>
    );
  }

  const shared = (await response.json()) as SharePayload;

  return (
    <main className="shell">
      <h1>Shared ArchiveVet snapshot</h1>
      <p>Expires {new Date(shared.expiresAt).toLocaleString()}</p>
      {shared.kind === "inspect" ? (
        <InspectSnapshot result={shared.payload as InspectResult} />
      ) : (
        <DiffSnapshot result={shared.payload as DiffResult} />
      )}
    </main>
  );
}

function InspectSnapshot({ result }: { result: InspectResult }) {
  const rows = flattenTree(result.tree);
  return (
    <section className="result-pane">
      <h2>
        {result.filename} — {result.summary.entryCount} entries
      </h2>
      {result.summary.flags.length ? (
        <p className="flags-banner danger">Flags: {result.summary.flags.join(", ")}</p>
      ) : null}
      <ul>
        {rows.slice(0, 200).map((entry) => (
          <li key={entry.path} className="tree-row">
            {entry.path} ({entry.size} B)
          </li>
        ))}
      </ul>
    </section>
  );
}

function DiffSnapshot({ result }: { result: DiffResult }) {
  return (
    <section className="result-pane">
      <h2>
        Diff — {result.added} added, {result.removed} removed, {result.contentChanged} content changed
      </h2>
      <ul>
        {result.changes.slice(0, 200).map((change) => (
          <li key={`${change.kind}-${change.path}`} className="tree-row">
            {change.kind}: {change.path}
          </li>
        ))}
      </ul>
    </section>
  );
}
