import { afterEach, describe, expect, it, vi } from "vitest";
import {
  ApiError,
  cancelBooking,
  checkIn,
  createBooking,
  createCheckInToken,
  getBookings,
  getCurrentUser,
  getRoomOccupancy,
  getRooms,
  logout,
  requestLoginOtp,
  verifyLoginOtp,
} from "../services/api.js";
import { parseCheckInQr } from "../services/checkin.js";
import {
  logout as logoutAuthApi,
  requestLoginOtp as requestAuthOtp,
  verifyLoginOtp as verifyAuthOtp,
} from "../services/authApi.ts";

afterEach(() => vi.unstubAllGlobals());

function response(status, payload) {
  return {
    status,
    ok: status >= 200 && status < 300,
    json: async () => payload,
  };
}

describe("shared Backend API", () => {
  it("connects the auth service to the real OTP request, verify, and logout endpoints", async () => {
    vi.stubEnv("VITE_USE_MOCK", "false");
    let currentToken = "old-token";
    const storage = {
      getItem: vi.fn(() => currentToken),
      setItem: vi.fn((key, value) => {
        currentToken = value;
      }),
      removeItem: vi.fn(() => {
        currentToken = null;
      }),
    };
    vi.stubGlobal("sessionStorage", storage);
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(response(202, { status: "otp_sent" }))
      .mockResolvedValueOnce(
        response(200, {
          access_token: "new-token",
          user: { id: 8, email: "student@uth.edu.vn" },
        }),
      )
      .mockResolvedValueOnce(response(204, null));
    vi.stubGlobal("fetch", fetchMock);

    await requestAuthOtp("student@uth.edu.vn");
    await verifyAuthOtp("student@uth.edu.vn", "123456");
    await logoutAuthApi();

    expect(fetchMock.mock.calls.map(([url]) => url)).toEqual([
      "/api/v1/auth/register",
      "/api/v1/auth/login",
      "/api/v1/auth/logout",
    ]);
    expect(fetchMock.mock.calls[0][1].headers.Authorization).toBeUndefined();
    expect(fetchMock.mock.calls[1][1].headers.Authorization).toBeUndefined();
    expect(fetchMock.mock.calls[2][1].headers.Authorization).toBe("Bearer new-token");
    expect(storage.setItem).toHaveBeenCalledWith(
      "seatsense_access_token",
      "new-token",
    );
    expect(storage.removeItem).toHaveBeenCalledWith("seatsense_access_token");
  });

  it("requests and verifies OTP without sending an existing bearer token", async () => {
    const storage = {
      getItem: vi.fn(() => "old-token"),
      setItem: vi.fn(),
    };
    vi.stubGlobal("sessionStorage", storage);
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(response(202, { status: "otp_sent" }))
      .mockResolvedValueOnce(
        response(200, {
          access_token: "new-token",
          user: { id: 8, email: "student@uth.edu.vn" },
        }),
      );
    vi.stubGlobal("fetch", fetchMock);

    await requestLoginOtp("student@uth.edu.vn");
    const user = await verifyLoginOtp("student@uth.edu.vn", "123456");

    expect(user.email).toBe("student@uth.edu.vn");
    expect(fetchMock.mock.calls[0][1].headers.Authorization).toBeUndefined();
    expect(fetchMock.mock.calls[1][1].headers.Authorization).toBeUndefined();
    expect(storage.setItem).toHaveBeenCalledWith(
      "seatsense_access_token",
      "new-token",
    );
  });

  it("sends the same bearer token for rooms, occupancy, bookings, and check-in", async () => {
    const storage = { getItem: () => "shared-token" };
    vi.stubGlobal("sessionStorage", storage);
    const fetchMock = vi.fn().mockResolvedValue(response(200, { items: [] }));
    vi.stubGlobal("fetch", fetchMock);

    await getCurrentUser();
    await getRooms();
    await getRoomOccupancy(3);
    await getBookings();
    await createBooking({
      roomId: 3,
      startsAt: "2026-11-17T02:00:00Z",
      endsAt: "2026-11-17T03:00:00Z",
      participantCount: 2,
    });
    await cancelBooking(7);
    await createCheckInToken(7);
    await checkIn({ bookingId: 7, qrToken: "secret" });
    await logout();

    const calls = fetchMock.mock.calls;
    expect(calls).toHaveLength(9);
    expect(
      calls.every(
        ([, options]) =>
          options.headers.Authorization === "Bearer shared-token",
      ),
    ).toBe(true);
    expect(calls.map(([url]) => url)).toEqual([
      "/api/v1/auth/me",
      "/api/v1/rooms?limit=100",
      "/api/v1/occupancy/rooms/3/latest",
      "/api/v1/bookings?limit=100",
      "/api/v1/bookings",
      "/api/v1/bookings/7",
      "/api/v1/bookings/7/check-in-token",
      "/api/v1/check-in",
      "/api/v1/auth/logout",
    ]);
  });

  it("surfaces API errors and accepts empty successful responses", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(
          response(409, {
            detail: {
              code: "booking_conflict",
              message: "This room is already booked during that time",
            },
          }),
        )
        .mockResolvedValueOnce({ status: 204, ok: true }),
    );

    await expect(cancelBooking(3)).rejects.toMatchObject({
      name: "ApiError",
      status: 409,
      code: "booking_conflict",
      message: "Phòng đã có lượt đặt trùng thời gian này.",
    });
    await expect(cancelBooking(3)).resolves.toBeNull();
    expect(new ApiError(401, "unauthorized", "expired")).toBeInstanceOf(Error);
  });
});

describe("check-in QR payload", () => {
  it("parses the JSON token format shared with Android", () => {
    expect(
      parseCheckInQr('{"booking_id":42,"qr_token":"one-time-secret"}'),
    ).toEqual({ bookingId: 42, qrToken: "one-time-secret" });
  });

  it.each([
    ["not json", "Mã QR không đúng định dạng JSON của SeatSense."],
    [
      '{"booking_id":0,"qr_token":"token"}',
      "Mã QR thiếu mã lượt đặt hoặc token check-in.",
    ],
    [
      '{"booking_id":42,"qr_token":""}',
      "Mã QR thiếu mã lượt đặt hoặc token check-in.",
    ],
  ])("rejects malformed QR data", (payload, message) => {
    expect(() => parseCheckInQr(payload)).toThrow(message);
  });
});
