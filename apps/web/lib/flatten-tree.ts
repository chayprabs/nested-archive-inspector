import type { ArchiveEntry } from "@archive-vet/shared-types";

export function flattenTree(nodes: ArchiveEntry[], prefix = ""): ArchiveEntry[] {
  const flat: ArchiveEntry[] = [];
  for (const node of nodes) {
    const path =
      prefix && !node.path.startsWith(prefix) ? `${prefix}/${node.path}`.replace("//", "/") : node.path;
    if (node.children?.length) {
      flat.push(...flattenTree(node.children, path));
    } else {
      flat.push({ ...node, path });
    }
  }
  return flat;
}
