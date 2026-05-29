export type SafetyFlag =
  | "path_traversal"
  | "symlink_escape"
  | "high_compression_ratio"
  | "encrypted"
  | "suspicious_file_count"
  | "suspicious_depth"
  | "polyglot";

export interface ArchiveEntry {
  path: string;
  size: number;
  compressedSize: number;
  mtime?: string | null;
  mode: number;
  mimeGuess?: string | null;
  sha256?: string | null;
  isDir: boolean;
  isSymlink: boolean;
  linkTarget?: string | null;
  isEncrypted: boolean;
  flags: SafetyFlag[];
  children?: ArchiveEntry[] | null;
}

export interface InspectSummary {
  entryCount: number;
  totalUncompressedBytes: number;
  totalCompressedBytes: number;
  maxDepth: number;
  formatGuess: string;
  flags: SafetyFlag[];
  blockedExtract: boolean;
}

export interface InspectResult {
  jobId: string;
  filename: string;
  tree: ArchiveEntry[];
  summary: InspectSummary;
}

export interface DiffChange {
  kind: "added" | "removed" | "content_changed" | "metadata_changed" | "renamed";
  path: string;
  otherPath?: string | null;
  sizeBefore?: number | null;
  sizeAfter?: number | null;
  sha256Before?: string | null;
  sha256After?: string | null;
}

export interface DiffResult {
  jobId: string;
  added: number;
  removed: number;
  contentChanged: number;
  metadataChanged: number;
  renamed: number;
  changes: DiffChange[];
}
