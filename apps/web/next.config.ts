import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  transpilePackages: [
    "@archive-vet/shared-ui",
    "@archive-vet/shared-types",
    "@archive-vet/shared-worker-runtime"
  ]
};

export default nextConfig;
