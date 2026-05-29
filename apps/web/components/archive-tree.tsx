"use client";

import type { ArchiveEntry } from "@archive-vet/shared-types";

export function ArchiveTree({
  nodes,
  depth = 0,
  onExpand,
  expandingPath
}: {
  nodes: ArchiveEntry[];
  depth?: number;
  onExpand?: (path: string) => void;
  expandingPath?: string | null;
}) {
  return (
    <ul style={{ listStyle: "none", margin: 0, paddingLeft: depth ? "1rem" : 0 }}>
      {nodes.map((node) => {
        const lazyArchive = node.isDir && node.children === null;
        const hasChildren = Boolean(node.children?.length);
        return (
          <li key={`${depth}-${node.path}`}>
            <div className="tree-row">
              <span>
                {lazyArchive || hasChildren ? "▸ " : "  "}
                {node.path}
              </span>
              <span>
                {node.size} B
                {node.flags.length ? ` · ${node.flags.join(",")}` : ""}
                {lazyArchive ? (
                  <button
                    type="button"
                    className="action secondary"
                    style={{ marginLeft: "0.5rem", padding: "0.2rem 0.6rem" }}
                    disabled={expandingPath === node.path}
                    onClick={() => onExpand?.(node.path)}
                  >
                    {expandingPath === node.path ? "Expanding…" : "Expand"}
                  </button>
                ) : null}
              </span>
            </div>
            {hasChildren ? (
              <ArchiveTree
                nodes={node.children!}
                depth={depth + 1}
                onExpand={onExpand}
                expandingPath={expandingPath}
              />
            ) : null}
          </li>
        );
      })}
    </ul>
  );
}

export function mergeExpandedBranch(
  tree: ArchiveEntry[],
  targetPath: string,
  children: ArchiveEntry[]
): ArchiveEntry[] {
  return tree.map((node) => {
    if (node.path === targetPath) {
      return { ...node, children, isDir: true };
    }
    if (node.children?.length) {
      return { ...node, children: mergeExpandedBranch(node.children, targetPath, children) };
    }
    return node;
  });
}
