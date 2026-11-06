const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "/api/v1").replace(
  /\/$/,
  "",
);
const OCCUPANCY_ENDPOINT =
  import.meta.env.VITE_OCCUPANCY_API_URL ??
  `${API_BASE_URL}/occupancy/current`;

export async function getApiHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
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
