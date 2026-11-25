import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import RoomCard from "../components/RoomCard";

describe("RoomCard", () => {
  it("shows only room name and current occupancy", () => {
    render(
      <RoomCard
        room={{
          id: 1,
          code: "DEMO-CS1-FREE-01",
          name: "Khu tự học CS1",
          capacity: 60,
          campus_code: "CS1",
          is_active: true,
          count: 48,
          updated_at: null,
          is_stale: false,
        }}
      />,
    );

    expect(screen.getByRole("article").textContent).toContain("Khu tự học CS1");
    expect(screen.getByRole("article").textContent).toContain("48");
  });

  it("shows unavailable when occupancy is missing", () => {
    render(
      <RoomCard
        room={{
          id: 2,
          code: "DEMO-CS3-FREE-01",
          name: "Khu tự học CS3",
          capacity: 50,
          campus_code: "CS3",
          is_active: true,
          count: null,
          updated_at: null,
          is_stale: false,
        }}
      />,
    );

    expect(screen.getByText("Chưa có dữ liệu")).toBeTruthy();
  });
});
