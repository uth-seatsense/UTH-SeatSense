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

describe("application routes", () => {
  it("renders OTP login rather than a placeholder", () => {
    const markup = renderRoute("/login");
    expect(markup).toContain("<h1>Đăng nhập bằng email</h1>");
    expect(markup).toContain('type="email"');
    expect(markup).toContain("Gửi mã OTP");
    expect(markup).not.toContain("skeleton-page");
  });

  it.each(["/rooms", "/reservation", "/my-bookings", "/checkin"])(
    "protects booking routes when signed out: %s",
    (location) => {
      const markup = renderRoute(location);
      expect(markup).toContain("<h1>Cần đăng nhập</h1>");
      expect(markup).toContain('href="/login"');
    },
  );

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

  it("renders the 404 page for unknown routes", () => {
    expect(renderRoute("/missing")).toContain("<h1>404</h1>");
  });
});
