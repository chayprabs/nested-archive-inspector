import type { ReactNode } from "react";

export function FileDrop({
  label,
  onFiles,
  accept
}: {
  label: string;
  onFiles: (files: FileList) => void;
  accept?: string;
}) {
  return (
    <label className="file-drop">
      <input
        type="file"
        accept={accept}
        onChange={(event) => {
          if (event.target.files?.length) {
            onFiles(event.target.files);
          }
        }}
      />
      <span>{label}</span>
    </label>
  );
}

export function ResultPane({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="result-pane">
      <h2>{title}</h2>
      {children}
    </section>
  );
}

export function SamplePicker({
  samples,
  onPick
}: {
  samples: { id: string; label: string }[];
  onPick: (id: string) => void;
}) {
  return (
    <div className="sample-picker">
      {samples.map((sample) => (
        <button key={sample.id} type="button" onClick={() => onPick(sample.id)}>
          {sample.label}
        </button>
      ))}
    </div>
  );
}
