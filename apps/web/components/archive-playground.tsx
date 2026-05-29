"use client";

import type { InspectResult } from "@archive-vet/shared-types";
import { FileDrop, ResultPane, SamplePicker } from "@archive-vet/shared-ui";
import { useMemo, useState } from "react";
import { Virtuoso } from "react-virtuoso";

const samples = [
  { id: "safe-release", label: "Safe release ZIP" },
  { id: "path-traversal", label: "Path traversal sample" },
  { id: "nested-release", label: "Nested release (.so)" },
  { id: "release-1.2.0", label: "Release 1.2.0 (diff)" },
  { id: "release-1.3.0", label: "Release 1.3.0 (diff)" }
];

export function ArchivePlayground() {
  const [result, setResult] = useState<InspectResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const rows = useMemo(() => result?.tree ?? [], [result]);

  async function inspectFile(file: File) {
    setBusy(true);
    setError(null);
    try {
      const body = new FormData();
      body.append("file", file, file.name);
      const response = await fetch("/api/worker/v1/inspect", { method: "POST", body });
      if (!response.ok) {
        throw new Error(`Inspect failed (${response.status})`);
      }
      setResult((await response.json()) as InspectResult);
    } catch (inspectError) {
      setError(inspectError instanceof Error ? inspectError.message : "Inspect failed");
      setResult(null);
    } finally {
      setBusy(false);
    }
  }

  async function loadSample(id: string) {
    const extension = id.startsWith("release-") || id === "nested-release" ? ".tar.gz" : ".zip";
    const response = await fetch(`/samples/${id}${extension}`);
    if (!response.ok) {
      setError(`Sample ${id} is not available yet`);
      return;
    }
    const blob = await response.blob();
    const mime = extension === ".tar.gz" ? "application/gzip" : "application/zip";
    await inspectFile(new File([blob], `${id}${extension}`, { type: mime }));
  }

  return (
    <section className="workbench" id="workbench">
      <FileDrop
        label={busy ? "Inspecting archive…" : "Drop an archive or click to browse"}
        accept=".zip,.tar,.tar.gz,.7z,.rar,.iso,.dmg,.cab"
        onFiles={(files) => void inspectFile(files[0]!)}
      />
      <SamplePicker samples={samples} onPick={(id) => void loadSample(id)} />
      {error ? <p className="flags-banner danger">{error}</p> : null}
      {result?.summary.flags.length ? (
        <div className="flags-banner danger" role="alert">
          Safety flags: {result.summary.flags.join(", ")}
          {result.summary.blockedExtract ? " — extraction blocked" : ""}
        </div>
      ) : null}
      {result ? (
        <ResultPane title={`${result.filename} (${result.summary.entryCount} entries)`}>
          <Virtuoso
            className="tree-panel"
            style={{ height: 420 }}
            data={rows}
            itemContent={(_index, entry) => (
              <div className="tree-row">
                <span>{entry.path}</span>
                <span>
                  {entry.size} B
                  {entry.flags.length ? ` · ${entry.flags.join(",")}` : ""}
                </span>
              </div>
            )}
          />
        </ResultPane>
      ) : null}
    </section>
  );
}
