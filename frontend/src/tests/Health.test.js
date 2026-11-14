import { afterEach, describe, expect, it, vi } from "vitest";
import { getApiHealth } from "../services/api.js";

afterEach(() => vi.unstubAllGlobals());

describe("backend health", () => {
  it("uses the API base path and forwards the abort signal", async () => {
    const data = { status: "ok", service: "backend" };
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => data,
    });
    vi.stubGlobal("fetch", fetchMock);
    const { signal } = new AbortController();
    await expect(getApiHealth({ signal })).resolves.toEqual(data);
    expect(fetchMock).toHaveBeenCalledWith("/api/v1/health", { signal });
  });

  it("reports HTTP failures rather than fake success", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 502 }),
    );
    await expect(getApiHealth()).rejects.toThrow(
      "Backend health request failed (502)",
    );
  });

  it("propagates network and invalid JSON errors", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
    await expect(getApiHealth()).rejects.toThrow("offline");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => {
          throw new SyntaxError("Invalid JSON");
        },
      }),
    );
    await expect(getApiHealth()).rejects.toThrow("Invalid JSON");
  });
});
