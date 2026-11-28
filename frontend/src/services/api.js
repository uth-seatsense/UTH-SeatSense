import { getCurrentOccupancy as getCurrentOccupancyData, getRooms as getMockRoomsResponse, isMockEnabled } from "./apiClient.ts";

export {
  getApiHealth,
  getCurrentOccupancy,
  normalizeOccupancy,
  USE_MOCK,
} from "./apiClient.ts";
export { isMockEnabled };
export async function getRoomOccupancyStatus({ signal, campus } = {}) {
  const result = await getCurrentOccupancyData({ signal });
  if (!result || !Array.isArray(result.rooms)) return null;

  const rooms = campus && result.campus?.toUpperCase() !== campus.toUpperCase()
    ? []
    : result.rooms;
  const updatedAt = result.last_updated ?? result.updatedAt ?? null;
  return {
    ...result,
    rooms,
    total_rooms: rooms.length,
    last_updated: updatedAt,
    updated_at: updatedAt,
  };
}

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "/api/v1").replace(
  /\/$/,
  "",
);
const AUTH_TOKEN_KEY = "seatsense_access_token";
const API_ERROR_MESSAGES = {
  email_not_allowed: "Email này chưa nằm trong danh sách được phép.",
  otp_resend_too_soon: "Vui lòng đợi trước khi yêu cầu mã OTP mới.",
  invalid_otp: "Mã OTP không đúng hoặc đã hết hạn.",
  email_auth_unavailable: "Đăng nhập OTP chưa được cấu hình trên máy chủ.",
  otp_delivery_failed: "Không gửi được email OTP. Vui lòng thử lại sau.",
  booking_conflict: "Phòng đã có lượt đặt trùng thời gian này.",
  daily_limit_exceeded: "Bạn đã đạt giới hạn đặt phòng trong ngày.",
  room_not_bookable: "Không thể đặt loại không gian này.",
  participant_limit_exceeded: "Số thành viên vượt sức chứa của phòng.",
  invalid_booking_time: "Giờ bắt đầu phải nằm trong tương lai.",
  invalid_booking_duration: "Thời lượng đặt phòng không nằm trong giới hạn.",
  booking_advance_limit: "Thời gian đặt vượt quá giới hạn đặt trước.",
  booking_cancel_window_closed: "Đã qua thời hạn hủy lượt đặt trực tuyến.",
  booking_not_active: "Lượt đặt này không còn hoạt động.",
  checkin_window_not_open: "Chưa đến thời gian check-in.",
  checkin_window_closed: "Đã hết thời gian check-in.",
  invalid_qr_token: "Mã QR không hợp lệ, đã hết hạn hoặc đã được sử dụng.",
};

export class ApiError extends Error {
  constructor(status, code, message) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

export function getAccessToken() {
  return globalThis.sessionStorage?.getItem(AUTH_TOKEN_KEY) ?? null;
}

export function saveAccessToken(token) {
  globalThis.sessionStorage?.setItem(AUTH_TOKEN_KEY, token);
}

export function clearAccessToken() {
  globalThis.sessionStorage?.removeItem(AUTH_TOKEN_KEY);
}

export async function requestApi(
  path,
  { method = "GET", body, signal, authenticated = true } = {},
) {
  const token = getAccessToken();
  const headers = { Accept: "application/json" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (authenticated && token) headers.Authorization = `Bearer ${token}`;

  const fetchOptions = {
    method,
    headers,
    signal,
  };
  if (body !== undefined) {
    fetchOptions.body = JSON.stringify(body);
  }
  const response = await fetch(`${API_BASE_URL}/${path.replace(/^\/+/, "")}`, fetchOptions);

  if (response.status === 204) {
    if (!response.ok) {
      throw new ApiError(
        response.status,
        "request_failed",
        "Yêu cầu thất bại.",
      );
    }
    return null;
  }

  let payload;
  try {
    payload = await response.json();
  } catch {
    if (response.ok) throw new Error("API không trả về JSON hợp lệ.");
    throw new ApiError(
      response.status,
      "request_failed",
      `Yêu cầu thất bại (HTTP ${response.status}).`,
    );
  }

  if (!response.ok) {
    if (response.status === 401 && authenticated && token) {
      globalThis.dispatchEvent?.(new Event("seatsense:unauthorized"));
    }
    const detail = payload?.detail ?? payload?.error;
    const code =
      typeof detail === "object" && detail !== null
        ? (detail.code ?? "request_failed")
        : "request_failed";
    const message =
      typeof detail === "object" && detail !== null
        ? (API_ERROR_MESSAGES[code] ??
          detail.message ??
          `Yêu cầu thất bại (HTTP ${response.status}).`)
        : `Yêu cầu thất bại (HTTP ${response.status}).`;
    throw new ApiError(response.status, code, message);
  }
  return payload;
}

export function requestLoginOtp(email) {
  return requestApi("auth/register", {
    method: "POST",
    body: { email },
    authenticated: false,
  });
}

export async function verifyLoginOtp(email, otp) {
  const result = await requestApi("auth/login", {
    method: "POST",
    body: { email, otp },
    authenticated: false,
  });
  saveAccessToken(result.access_token);
  return result.user;
}

export function getCurrentUser() {
  const mockEnabled = isMockEnabled();
  console.log("🔍 getCurrentUser - isMockEnabled:", mockEnabled, "VITE_USE_MOCK:", import.meta.env.VITE_USE_MOCK);

  if (mockEnabled) {
    try {
      const savedProfile = globalThis.sessionStorage?.getItem("seatsense_mock_user");
      if (savedProfile) return Promise.resolve(JSON.parse(savedProfile));
    } catch {
      globalThis.sessionStorage?.removeItem("seatsense_mock_user");
    }
    return Promise.resolve({
      id: 1,
      email: "test@ut.edu.vn",
      display_name: "Test User",
      created_at: new Date().toISOString(),
    });
  }
  console.log("⚠️  Making real API call to auth/me");
  return requestApi("auth/me");
}

export function logout() {
  return requestApi("auth/logout", { method: "POST" });
}

export async function getRooms({ signal } = {}) {
  const response = isMockEnabled()
    ? await getMockRoomsResponse({ signal })
    : await requestApi("rooms?limit=100", { signal });
  const rooms = [...response.items];

  return Object.assign(rooms, {
    items: [...response.items],
    limit: response.limit,
    offset: response.offset,
    total: response.total,
  });
}

export async function getRoomById(roomId, { signal } = {}) {
  if (isMockEnabled()) {
    const rooms = await getMockRoomsResponse({ signal });
    return rooms.items.find((room) => room.id === roomId);
  }
  return requestApi(`rooms/${roomId}`, { signal });
}

export function getRoomOccupancy(roomId, { signal } = {}) {
  return requestApi(`occupancy/rooms/${roomId}/latest`, { signal });
}

export async function getBookings({ signal } = {}) {
  const result = await requestApi("bookings?limit=100", { signal });
  return result.items;
}

export function createBooking({ roomId, startsAt, endsAt, participantCount }) {
  return requestApi("bookings", {
    method: "POST",
    body: {
      room_id: roomId,
      starts_at: startsAt,
      ends_at: endsAt,
      participant_count: participantCount,
    },
  });
}

export function cancelBooking(bookingId) {
  return requestApi(`bookings/${bookingId}`, { method: "DELETE" });
}

export function createCheckInToken(bookingId) {
  return requestApi(`bookings/${bookingId}/check-in-token`, {
    method: "POST",
  });
}

export function checkIn({ bookingId, qrToken }) {
  return requestApi("check-in", {
    method: "POST",
    body: { booking_id: bookingId, qr_token: qrToken },
  });
}
