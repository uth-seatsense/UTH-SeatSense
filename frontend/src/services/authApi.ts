import authMock from "../../mocks/auth.json";
import {
  ApiError,
  clearAccessToken,
  isMockEnabled,
  requestApi,
  saveAccessToken,
} from "./api.js";

type MockInbox = {
  to: string;
  subject: string;
  otp: string;
};

type OtpRequestResult = {
  status: "otp_sent";
  expiresInSeconds: number;
  resendCooldownSeconds: number;
  mockInbox?: MockInbox;
};

type AuthUser = {
  id: number | string;
  email: string;
  display_name: string;
  created_at?: string;
  role?: string;
};

const challenges = new Map<string, { expiresAt: number; lastSentAt: number }>();

export async function requestLoginOtp(email: string): Promise<OtpRequestResult> {
  const normalizedEmail = email.trim().toLowerCase();
  if (!isMockEnabled()) {
    return requestApi("auth/register", {
      method: "POST",
      body: { email: normalizedEmail },
      authenticated: false,
    });
  }

  const account = authMock.accounts.find(
    (candidate) => candidate.email.toLowerCase() === normalizedEmail,
  );
  if (!account) {
    throw new ApiError(
      422,
      "email_not_allowed",
      "Email kh\u00f4ng c\u00f3 trong danh s\u00e1ch \u0111\u0103ng nh\u1eadp th\u1eed.",
    );
  }

  const now = Date.now();
  const previous = challenges.get(normalizedEmail);
  if (
    previous &&
    now - previous.lastSentAt < authMock.resendCooldownSeconds * 1000
  ) {
    throw new ApiError(
      429,
      "otp_resend_too_soon",
      "Vui l\u00f2ng \u0111\u1ee3i tr\u01b0\u1edbc khi g\u1eedi l\u1ea1i m\u00e3.",
    );
  }
  challenges.set(normalizedEmail, {
    expiresAt: now + authMock.otpTtlSeconds * 1000,
    lastSentAt: now,
  });

  return {
    status: "otp_sent",
    expiresInSeconds: authMock.otpTtlSeconds,
    resendCooldownSeconds: authMock.resendCooldownSeconds,
    mockInbox: {
      to: normalizedEmail,
      subject: "M\u00e3 x\u00e1c th\u1ef1c \u0111\u0103ng nh\u1eadp UTH-SeatSense",
      otp: account.otp,
    },
  };
}

export async function verifyLoginOtp(email: string, otp: string): Promise<AuthUser> {
  const normalizedEmail = email.trim().toLowerCase();
  if (!isMockEnabled()) {
    const result = await requestApi("auth/login", {
      method: "POST",
      body: { email: normalizedEmail, otp },
      authenticated: false,
    });
    saveAccessToken(result.access_token);
    return result.user;
  }

  const account = authMock.accounts.find(
    (candidate) => candidate.email.toLowerCase() === normalizedEmail,
  );
  const challenge = challenges.get(normalizedEmail);
  if (!account || !challenge) {
    throw new ApiError(
      401,
      "invalid_otp",
      "Y\u00eau c\u1ea7u m\u00e3 OTP m\u1edbi tr\u01b0\u1edbc khi \u0111\u0103ng nh\u1eadp.",
    );
  }
  if (Date.now() >= challenge.expiresAt) {
    challenges.delete(normalizedEmail);
    throw new ApiError(
      401,
      "otp_expired",
      "M\u00e3 OTP \u0111\u00e3 h\u1ebft h\u1ea1n. H\u00e3y g\u1eedi l\u1ea1i m\u00e3 m\u1edbi.",
    );
  }
  if (!/^\d{6}$/.test(otp) || otp !== account.otp) {
    throw new ApiError(
      401,
      "invalid_otp",
      "M\u00e3 OTP kh\u00f4ng \u0111\u00fang. Vui l\u00f2ng ki\u1ec3m tra l\u1ea1i.",
    );
  }

  challenges.delete(normalizedEmail);
  saveAccessToken("mock-token-" + Date.now());
  return {
    id: 1,
    email: normalizedEmail,
    display_name: account.displayName,
    created_at: new Date().toISOString(),
  };
}

export async function logout(): Promise<void> {
  try {
    if (!isMockEnabled()) {
      await requestApi("auth/logout", { method: "POST" });
    }
  } finally {
    clearAccessToken();
  }
}

export function resetAuthMock(): void {
  challenges.clear();
}
