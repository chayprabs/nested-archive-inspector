import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ArchiveVet — nested archive inspector",
  description:
    "Open and safely inspect ZIP, 7z, RAR, TAR, ISO, DMG and nested archives online with zip-bomb and path-traversal protection."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
