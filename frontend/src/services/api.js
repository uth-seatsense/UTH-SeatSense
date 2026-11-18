const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "/api/v1").replace(
  /\/$/,
  "",
);
const OCCUPANCY_ENDPOINT =
  import.meta.env.VITE_OCCUPANCY_API_URL ?? `${API_BASE_URL}/occupancy/current`;
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

  const response = await fetch(`${API_BASE_URL}/${path.replace(/^\/+/, "")}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
    signal,
  });

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
  return requestApi("auth/me");
}

export function logout() {
  return requestApi("auth/logout", { method: "POST" });
}

export async function getRooms({ signal } = {}) {
  const result = await requestApi("rooms?limit=100", { signal });
  return result.items;
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

export async function getApiHealth({ signal } = {}) {
  const response = await fetch(`${API_BASE_URL}/health`, { signal });
  if (!response.ok) {
    throw new Error(`Backend health request failed (${response.status})`);
  }
  return response.json();
}

export async function getCurrentOccupancy({ signal } = {}) {
  const url = new URL(OCCUPANCY_ENDPOINT, window.location.origin);

  const response = await fetch(url, { signal });
  if (!response.ok) {
    throw new Error(`API trả về lỗi HTTP ${response.status}`);
  }

  let payload;
  try {
    payload = await response.json();
  } catch {
    throw new Error("API không trả về JSON hợp lệ");
  }

  return normalizeOccupancy(payload);
}

export function normalizeOccupancy(payload) {
  if (payload == null || (Array.isArray(payload) && payload.length === 0)) {
    return null;
  }

  const record = payload.data ?? payload;
  if (!record || typeof record !== "object" || Array.isArray(record)) {
    throw new Error("Dữ liệu API không đúng định dạng");
  }

  const countField = [
    "current_count",
    "people_count",
    "occupancy_count",
    "count",
  ].find((field) => Object.hasOwn(record, field));

  if (!countField || record[countField] == null) {
    return null;
  }

  const count = record[countField];
  if (!Number.isInteger(count) || count < 0) {
    throw new Error("API trả về số người không hợp lệ");
  }

  const updatedAt =
    record.updated_at ??
    record.last_updated ??
    record.updatedAt ??
    record.timestamp ??
    null;

  return {
    count,
    updatedAt: typeof updatedAt === "string" ? updatedAt : null,
    location:
      typeof record.location === "string"
        ? record.location
        : typeof record.location_name === "string"
          ? record.location_name
          : null,
  };
}
