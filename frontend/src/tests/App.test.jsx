import { describe, expect, it } from "vitest";
import App from "../App.jsx";

describe("App", () => {
  it("renders the SeatSense welcome content", () => {
    const section = App().props.children;

    expect(section.type).toBe("section");
    expect(section.props.children[1].props.children).toBe("UTH-SeatSense");
  });
});
