import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import HealthPage from "../src/pages/HealthPage.jsx";
import { getApiHealth } from "../src/services/api.js";

vi.mock("../src/services/api.js", () => ({
  getApiHealth: vi.fn(),
}));

describe("HealthPage component", () => {
  beforeEach(() => {
    vi.mocked(getApiHealth).mockResolvedValue({
      status: "ok",
      service: "backend",
    });
  });

  it("shows a successful health response", async () => {
    render(<HealthPage />);

    expect(await screen.findByText("Kết nối backend thành công.")).toBeTruthy();
    expect(screen.getByText(/"service": "backend"/)).toBeTruthy();
  });
});
