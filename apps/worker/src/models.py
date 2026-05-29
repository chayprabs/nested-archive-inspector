from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

SafetyFlag = Literal[
    "path_traversal",
    "symlink_escape",
    "high_compression_ratio",
    "encrypted",
    "suspicious_file_count",
    "suspicious_depth",
    "polyglot",
]


class ArchiveEntry(BaseModel):
    path: str
    size: int = 0
    compressedSize: int = 0
    mtime: str | None = None
    mode: int = 0
    mimeGuess: str | None = None
    sha256: str | None = None
    isDir: bool = False
    isSymlink: bool = False
    linkTarget: str | None = None
    isEncrypted: bool = False
    flags: list[SafetyFlag] = Field(default_factory=list)
    children: list["ArchiveEntry"] | None = None


class InspectSummary(BaseModel):
    entryCount: int
    totalUncompressedBytes: int
    totalCompressedBytes: int
    maxDepth: int
    formatGuess: str
    flags: list[SafetyFlag]
    blockedExtract: bool


class InspectResult(BaseModel):
    jobId: str
    filename: str
    tree: list[ArchiveEntry]
    summary: InspectSummary


class DiffChange(BaseModel):
    kind: Literal["added", "removed", "content_changed", "metadata_changed", "renamed"]
    path: str
    otherPath: str | None = None
    sizeBefore: int | None = None
    sizeAfter: int | None = None
    sha256Before: str | None = None
    sha256After: str | None = None


class DiffResult(BaseModel):
    jobId: str
    added: int
    removed: int
    contentChanged: int
    metadataChanged: int
    renamed: int
    changes: list[DiffChange]
