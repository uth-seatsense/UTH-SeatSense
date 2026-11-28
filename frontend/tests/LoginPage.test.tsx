import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import LoginPage from "../src/pages/LoginPage.tsx";

const mocks = vi.hoisted(() => ({
  login: vi.fn(),
  requestLoginOtp: vi.fn(),
}));

vi.mock("../src/auth/AuthContext.jsx", () => ({
  useAuth: () => ({ user: null, login: mocks.login }),
}));

vi.mock("../src/services/authApi.ts", () => ({
  requestLoginOtp: mocks.requestLoginOtp,
}));

const testEmail = "21510509213@ut.edu.vn";

function renderLogin() {
  return render(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>,
  );
}

function getFormFor(label: RegExp) {
  const input = screen.getByLabelText(label);
  const form = input.closest("form");
  if (!form) throw new Error("Expected the field to be inside a form");
  return form;
}

async function requestCode(expiresInSeconds = 300) {
  mocks.requestLoginOtp.mockResolvedValueOnce({
    status: "otp_sent",
    expiresInSeconds,
    resendCooldownSeconds: 60,
    mockInbox: { to: testEmail, otp: "482910" },
  });
  fireEvent.change(screen.getByLabelText(/Email/), {
    target: { value: testEmail },
  });
  await act(async () => {
    fireEvent.submit(getFormFor(/Email/));
  });
}

beforeEach(() => {
  mocks.login.mockReset();
  mocks.requestLoginOtp.mockReset();
});

afterEach(() => {
  vi.useRealTimers();
});

describe("LoginPage OTP flow", () => {
  it("shows the mock inbox code and signs in with a valid OTP", async () => {
    mocks.login.mockResolvedValue(undefined);
    renderLogin();
    await requestCode();

    expect(screen.getByRole("status").textContent).toContain("482910");
    fireEvent.change(screen.getByLabelText(/OTP/), {
      target: { value: "482910" },
    });
    await act(async () => {
      fireEvent.submit(getFormFor(/OTP/));
    });

    expect(mocks.login).toHaveBeenCalledWith(testEmail, "482910");
  });

  it("shows a wrong-code message for an invalid OTP", async () => {
    mocks.login.mockRejectedValue(Object.assign(new Error("invalid"), { code: "invalid_otp" }));
    renderLogin();
    await requestCode();
    fireEvent.change(screen.getByLabelText(/OTP/), {
      target: { value: "111111" },
    });
    await act(async () => {
      fireEvent.submit(getFormFor(/OTP/));
    });

    expect(screen.getByRole("alert").textContent).toContain("M\u00e3 OTP kh\u00f4ng \u0111\u00fang");
  });

  it("shows an expired-code message when the OTP has expired", async () => {
    renderLogin();
    await requestCode(0);
    fireEvent.change(screen.getByLabelText(/OTP/), {
      target: { value: "482910" },
    });
    await act(async () => {
      fireEvent.submit(getFormFor(/OTP/));
    });

    expect(screen.getByRole("alert").textContent).toContain("M\u00e3 OTP \u0111\u00e3 h\u1ebft h\u1ea1n");
    expect(mocks.login).not.toHaveBeenCalled();
  });

  it("shows a wrong-code message when the local countdown is still active", async () => {
    mocks.login.mockRejectedValue(
      Object.assign(new Error("expired"), { code: "otp_expired" }),
    );
    renderLogin();
    await requestCode();
    fireEvent.change(screen.getByLabelText(/OTP/), {
      target: { value: "365784" },
    });
    await act(async () => {
      fireEvent.submit(getFormFor(/OTP/));
    });

    const message = screen.getByRole("alert").textContent ?? "";
    expect(message).toContain("M\u00e3 OTP kh\u00f4ng \u0111\u00fang");
    expect(message).not.toContain("M\u00e3 OTP \u0111\u00e3 h\u1ebft h\u1ea1n");
  });

  it("starts a 60-second cooldown and requests another code after it ends", async () => {
    vi.useFakeTimers();
    const { container } = renderLogin();
    await requestCode();
    const resendButton = container.querySelector(".lp-resend-btn") as HTMLButtonElement;
    expect(resendButton.textContent).toContain("60s");
    expect(resendButton.disabled).toBe(true);

    await act(async () => {
      await vi.advanceTimersByTimeAsync(60_000);
    });
    expect(resendButton.disabled).toBe(false);

    mocks.requestLoginOtp.mockResolvedValueOnce({
      status: "otp_sent",
      expiresInSeconds: 300,
      resendCooldownSeconds: 60,
      mockInbox: { to: testEmail, otp: "482910" },
    });
    await act(async () => {
      fireEvent.click(resendButton);
      await Promise.resolve();
    });

    expect(mocks.requestLoginOtp).toHaveBeenCalledTimes(2);
    expect(resendButton.disabled).toBe(true);
  });
});
