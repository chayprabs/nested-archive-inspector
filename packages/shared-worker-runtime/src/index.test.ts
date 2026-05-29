import { describe, expect, it } from "vitest";
import { resolveWorkerBaseUrl } from "./index";

describe("resolveWorkerBaseUrl", () => {
  it("prefers ARCHIVEVET_WORKER_URL", () => {
    expect(
      resolveWorkerBaseUrl({
        ARCHIVEVET_WORKER_URL: "http://worker:8000/",
        NEXT_PUBLIC_ARCHIVEVET_WORKER_URL: "http://ignored"
      })
    ).toBe("http://worker:8000");
  });
});
