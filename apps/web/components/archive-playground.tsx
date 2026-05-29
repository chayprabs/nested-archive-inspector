"use client";

import type { DiffResult, InspectResult } from "@archive-vet/shared-types";
import { FileDrop, ResultPane, SamplePicker } from "@archive-vet/shared-ui";
import { ArchiveTree, mergeExpandedBranch } from "@/components/archive-tree";
import { useState } from "react";
import { Virtuoso } from "react-virtuoso";

const samples = [
  { id: "safe-release", label: "Safe release ZIP" },
  { id: "path-traversal", label: "Path traversal sample" },
  { id: "zip-bomb-small", label: "Zip bomb (small)" },
  { id: "nested-release", label: "Nested release (.so)" },
  { id: "nested-bundle", label: "Nested bundle ZIP" },
  { id: "encrypted", label: "Encrypted 7z (demo)" },
  { id: "iso-sample", label: "ISO sample" },
  { id: "release-1.2.0", label: "Release 1.2.0 (diff)" },
  { id: "release-1.3.0", label: "Release 1.3.0 (diff)" }
];

type Mode = "inspect" | "diff";

export function ArchivePlayground() {
  const [mode, setMode] = useState<Mode>("inspect");
  const [result, setResult] = useState<InspectResult | null>(null);
  const [diff, setDiff] = useState<DiffResult | null>(null);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [urlInput, setUrlInput] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [lastFile, setLastFile] = useState<File | null>(null);
  const [expandingPath, setExpandingPath] = useState<string | null>(null);

  async function inspectFile(file: File) {
    setBusy(true);
    setError(null);
    setShareUrl(null);
    try {
      const body = new FormData();
      body.append("file", file, file.name);
      if (password) {
        body.append("password", password);
      }
      const response = await fetch("/api/worker/v1/inspect", { method: "POST", body });
      if (!response.ok) {
        throw new Error(`Inspect failed (${response.status})`);
      }
      const payload = (await response.json()) as InspectResult;
      setResult(payload);
      setLastFile(file);
      setDiff(null);
    } catch (inspectError) {
      setError(inspectError instanceof Error ? inspectError.message : "Inspect failed");
      setResult(null);
    } finally {
      setBusy(false);
    }
  }

  async function expandNestedEntry(entryPath: string) {
    if (!lastFile || !result) {
      return;
    }
    setExpandingPath(entryPath);
    setError(null);
    try {
      const body = new FormData();
      body.append("file", lastFile, lastFile.name);
      body.append("entry_path", entryPath);
      if (password) {
        body.append("password", password);
      }
      const response = await fetch("/api/worker/v1/inspect/expand", { method: "POST", body });
      if (!response.ok) {
        throw new Error(`Expand failed (${response.status})`);
      }
      const children = (await response.json()) as InspectResult["tree"];
      setResult({
        ...result,
        tree: mergeExpandedBranch(result.tree, entryPath, children)
      });
    } catch (expandError) {
      setError(expandError instanceof Error ? expandError.message : "Expand failed");
    } finally {
      setExpandingPath(null);
    }
  }

  async function inspectUrl() {
    if (!urlInput.trim()) {
      return;
    }
    setBusy(true);
    setError(null);
    setShareUrl(null);
    try {
      const body = new FormData();
      body.append("url", urlInput.trim());
      if (password) {
        body.append("password", password);
      }
      const response = await fetch("/api/worker/v1/inspect/url", { method: "POST", body });
      if (!response.ok) {
        throw new Error(`URL inspect failed (${response.status})`);
      }
      const payload = (await response.json()) as InspectResult;
      setResult(payload);
      setLastFile(null);
      setDiff(null);
    } catch (inspectError) {
      setError(inspectError instanceof Error ? inspectError.message : "URL inspect failed");
      setResult(null);
    } finally {
      setBusy(false);
    }
  }

  async function runDiff(left: File, right: File) {
    setBusy(true);
    setError(null);
    setShareUrl(null);
    try {
      const body = new FormData();
      body.append("left", left, left.name);
      body.append("right", right, right.name);
      const response = await fetch("/api/worker/v1/diff", { method: "POST", body });
      if (!response.ok) {
        throw new Error(`Diff failed (${response.status})`);
      }
      setDiff((await response.json()) as DiffResult);
      setResult(null);
    } catch (diffError) {
      setError(diffError instanceof Error ? diffError.message : "Diff failed");
      setDiff(null);
    } finally {
      setBusy(false);
    }
  }

  async function createShareLink() {
    const payload = result ?? diff;
    if (!payload) {
      return;
    }
    const kind = result ? "inspect" : "diff";
    const response = await fetch("/api/worker/v1/share", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ kind, payload })
    });
    if (!response.ok) {
      setError(`Share failed (${response.status})`);
      return;
    }
    const body = (await response.json()) as { sharePath: string };
    setShareUrl(`${window.location.origin}${body.sharePath}`);
  }

  async function loadSample(id: string) {
    let extension = ".zip";
    if (id.startsWith("release-") || id === "nested-release") {
      extension = ".tar.gz";
    } else if (id === "encrypted") {
      extension = ".7z";
    } else if (id === "iso-sample") {
      extension = ".iso";
    }
    const response = await fetch(`/samples/${id}${extension}`);
    if (!response.ok) {
      setError(`Sample ${id} is not available yet`);
      return;
    }
    const blob = await response.blob();
    await inspectFile(new File([blob], `${id}${extension}`));
  }

  return (
    <section className="workbench" id="workbench">
      <div className="sample-picker">
        <button type="button" className={mode === "inspect" ? "action" : "action secondary"} onClick={() => setMode("inspect")}>
          Inspect
        </button>
        <button type="button" className={mode === "diff" ? "action" : "action secondary"} onClick={() => setMode("diff")}>
          Diff two archives
        </button>
      </div>

      {mode === "inspect" ? (
        <>
          <FileDrop
            label={busy ? "Inspecting archive…" : "Drop an archive or click to browse"}
            accept=".zip,.tar,.tar.gz,.7z,.rar,.iso,.dmg,.cab"
            onFiles={(files) => void inspectFile(files[0]!)}
          />
          <label className="file-drop">
            <span>Archive URL (HTTPS)</span>
            <input
              type="url"
              value={urlInput}
              onChange={(event) => setUrlInput(event.target.value)}
              placeholder="https://example.com/archive.zip"
              style={{ width: "100%", marginTop: "0.5rem" }}
            />
          </label>
          <button type="button" className="action" onClick={() => void inspectUrl()} disabled={busy}>
            Inspect URL
          </button>
          <label className="file-drop">
            <span>Password (encrypted archives)</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="off"
              style={{ width: "100%", marginTop: "0.5rem" }}
            />
          </label>
        </>
      ) : (
        <DiffDrop onDiff={(left, right) => void runDiff(left, right)} busy={busy} />
      )}

      <SamplePicker samples={samples} onPick={(id) => void loadSample(id)} />
      {error ? <p className="flags-banner danger">{error}</p> : null}
      {(result || diff) && (
        <button type="button" className="action secondary" onClick={() => void createShareLink()}>
          Create share link
        </button>
      )}
      {shareUrl ? (
        <p className="result-pane">
          Share:{" "}
          <a href={shareUrl}>{shareUrl}</a>
        </p>
      ) : null}

      {result?.summary.flags.length ? (
        <div className="flags-banner danger" role="alert">
          Safety flags: {result.summary.flags.join(", ")}
          {result.summary.blockedExtract ? " — extraction blocked" : ""}
        </div>
      ) : null}

      {result ? (
        <ResultPane title={`${result.filename} (${result.summary.entryCount} entries)`}>
          <div className="tree-panel" style={{ maxHeight: 420, overflow: "auto" }}>
            <ArchiveTree
              nodes={result.tree}
              onExpand={(path) => void expandNestedEntry(path)}
              expandingPath={expandingPath}
            />
          </div>
        </ResultPane>
      ) : null}

      {diff ? (
        <ResultPane
          title={`Diff — ${diff.added} added, ${diff.removed} removed, ${diff.contentChanged} changed`}
        >
          <Virtuoso
            className="tree-panel"
            style={{ height: 420 }}
            data={diff.changes}
            itemContent={(_index, change) => (
              <div className="tree-row">
                <span>
                  {change.kind}: {change.path}
                </span>
              </div>
            )}
          />
        </ResultPane>
      ) : null}
    </section>
  );
}

function DiffDrop({
  onDiff,
  busy
}: {
  onDiff: (left: File, right: File) => void;
  busy: boolean;
}) {
  const [left, setLeft] = useState<File | null>(null);
  const [right, setRight] = useState<File | null>(null);

  return (
    <div className="workbench">
      <FileDrop
        label={left ? `Left: ${left.name}` : "Drop left archive"}
        onFiles={(files) => setLeft(files[0] ?? null)}
      />
      <FileDrop
        label={right ? `Right: ${right.name}` : "Drop right archive"}
        onFiles={(files) => setRight(files[0] ?? null)}
      />
      <button
        type="button"
        className="action"
        disabled={!left || !right || busy}
        onClick={() => left && right && onDiff(left, right)}
      >
        Run diff
      </button>
    </div>
  );
}
