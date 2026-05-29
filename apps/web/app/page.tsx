import { ArchivePlayground } from "../components/archive-playground";

const repoUrl = "https://github.com/chayprabs/nested-archive-inspector";

export default function HomePage() {
  return (
    <main className="shell">
      <nav className="topbar" aria-label="Primary">
        <strong>ArchiveVet</strong>
        <a href={repoUrl} rel="noreferrer" target="_blank">
          Source
        </a>
      </nav>
      <header className="hero">
        <p className="eyebrow">AGPL-3.0</p>
        <h1>Inspect nested archives safely before you extract them.</h1>
        <p>
          Walk ZIP, TAR, 7z, RAR, ISO, DMG and more with zip-bomb, path-traversal,
          and symlink protection. Select files to extract or diff two release archives.
        </p>
      </header>
      <ArchivePlayground />
    </main>
  );
}
