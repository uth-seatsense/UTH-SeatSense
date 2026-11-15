import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { StaticRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import App from "../App.jsx";

function renderRoute(location) {
  return renderToStaticMarkup(
    createElement(StaticRouter, { location }, createElement(App)),
  );
}

describe("skeleton routes", () => {
  it.each([
    "/login",
    "/rooms",
    "/reservation",
    "/my-bookings",
    "/checkin",
    "/health",
  ])("uses consistent skeleton spacing at %s", (location) => {
    expect(renderRoute(location)).toContain('<main class="skeleton-page">');
  });

  it.each([
    ["/", "Tổng quan Thư viện UTH"],
    ["/login", "Đăng nhập"],
    ["/rooms", "Phòng học"],
    ["/reservation", "Đặt chỗ"],
    ["/my-bookings", "Lịch đặt của tôi"],
    ["/checkin", "Check-in"],
    ["/dashboard", "Tổng quan Thư viện UTH"],
    ["/health", "Health Check"],
    ["/missing", "404"],
  ])("renders the page heading at %s", (location, heading) => {
    expect(renderRoute(location)).toContain(`<h1>${heading}</h1>`);
  });

  it.each([
    ["/", true],
    ["/dashboard", true],
    ["/dashboard/", true],
    ["/login", false],
    ["/rooms", false],
    ["/health", false],
  ])("reserves sidebar space correctly at %s", (location, hasSidebar) => {
    expect(renderRoute(location).includes("app-navigation--dashboard")).toBe(
      hasSidebar,
    );
  });

  it("does not render the legacy Home header behind the fixed sidebar", () => {
    const home = renderRoute("/");
    expect(home).not.toContain('class="site-header"');
    expect(home.match(/class="app-shell"/g)).toHaveLength(1);
    expect(home.match(/<main/g)).toHaveLength(1);
  });

  it("marks the current navigation link", () => {
    expect(renderRoute("/login")).toMatch(
      /<a[^>]*aria-current="page"[^>]*href="\/login"/,
    );
  });

  it("hides Health from navigation while keeping the health route available", () => {
    expect(renderRoute("/")).not.toContain('href="/health"');
    expect(renderRoute("/health")).toContain("<h1>Health Check</h1>");
  });

  it("places Login after the main navigation group", () => {
    expect(renderRoute("/")).toMatch(
      /<\/div><a class="app-navigation-login" href="\/login"[^>]*>Đăng nhập<\/a><\/nav>/,
    );
  });

  it.each(["/", "/dashboard"])(
    "links the sidebar booking action to the reservation route at %s",
    (location) => {
      expect(renderRoute(location)).toMatch(
        /<a class="side-link" href="\/reservation"[^>]*>/,
      );
      expect(renderRoute(location)).not.toContain('href="#rooms"');
    },
  );
});
