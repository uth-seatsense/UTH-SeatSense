import occupancyFresh from "../../mocks/occupancy.fresh.json";
import occupancyOffline from "../../mocks/occupancy.offline.json";
import occupancyStale from "../../mocks/occupancy.stale.json";
import roomsMock from "../../mocks/rooms.json";

type MockOccupancyState = "fresh" | "stale" | "offline";

type OccupancyRoom = {
  room_id: number;
  room_code: string;
  room_name: string;
  room_type: string;
  capacity: number;
  current_count: number | null;
  available_seats: number | null;
  occupancy_level: "low" | "medium" | "high" | null;
  recorded_at: string | null;
  updated_at: string | null;
  is_stale: boolean;
  device_status: "online" | "offline" | "error";
};

type OccupancyResponse = {
  campus: string;
  rooms: OccupancyRoom[];
  total_rooms: number;
  last_updated: string | null;
};

type Room = {
  id: number;
  code: string;
  name: string;
  capacity: number;
  campus_id: number | null;
  campus_code: string | null;
  building: string | null;
  is_active: boolean;
};

type RoomsResponse = {
  items: Room[];
  limit: number;
  offset: number;
  total: number;
};

type NormalizedOccupancy = {
  count: number;
  updatedAt: string | null;
  location: string | null;
};

type OccupancyResult = OccupancyResponse & {
  count: number | null;
  updatedAt: string | null;
  location: string | null;
};

type RequestOptions = {
  signal?: AbortSignal;
};

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "/api/v1").replace(
  /\/$/,
  "",
);
const OCCUPANCY_ENDPOINT =
  import.meta.env.VITE_OCCUPANCY_API_URL ?? `${API_BASE_URL}/occupancy/current`;
const MOCK_ROOMS: RoomsResponse = roomsMock;
const MOCK_OCCUPANCY: Record<MockOccupancyState, OccupancyResponse> = {
  fresh: occupancyFresh as OccupancyResponse,
  stale: occupancyStale as OccupancyResponse,
  offline: occupancyOffline as OccupancyResponse,
};

export function isMockEnabled(): boolean {
  return import.meta.env.VITE_USE_MOCK === "true";
}

export const USE_MOCK = isMockEnabled();

function getMockOccupancyState(state?: MockOccupancyState): MockOccupancyState {
  const configuredState = import.meta.env.VITE_MOCK_OCCUPANCY_STATE;
  const selectedState = state ?? configuredState ?? "fresh";

  if (!Object.hasOwn(MOCK_OCCUPANCY, selectedState)) {
    throw new Error(
      `VITE_MOCK_OCCUPANCY_STATE must be fresh, stale, or offline (received "${selectedState}")`,
    );
  }

  return selectedState as MockOccupancyState;
}

async function readJson(
  response: Response,
  parseErrorMessage?: string,
): Promise<unknown> {
  try {
    return await response.json();
  } catch (error) {
    if (error instanceof SyntaxError && parseErrorMessage) {
      throw new Error(parseErrorMessage);
    }
    throw error;
  }
}

export async function getApiHealth({
  signal,
}: RequestOptions = {}): Promise<unknown> {
  if (isMockEnabled()) {
    return { status: "ok", service: "backend" };
  }

  const response = await fetch(`${API_BASE_URL}/health`, { signal });
  if (!response.ok) {
    throw new Error(`Backend health request failed (${response.status})`);
  }
  return readJson(response);
}

function parseRoomsResponse(payload: unknown): RoomsResponse {
  if (
    typeof payload !== "object" ||
    payload === null ||
    !("items" in payload) ||
    !Array.isArray(payload.items) ||
    !("limit" in payload) ||
    !Number.isInteger(payload.limit) ||
    !("offset" in payload) ||
    !Number.isInteger(payload.offset) ||
    !("total" in payload) ||
    !Number.isInteger(payload.total) ||
    !payload.items.every(
      (room) =>
        typeof room === "object" &&
        room !== null &&
        "id" in room &&
        Number.isInteger(room.id) &&
        "code" in room &&
        typeof room.code === "string" &&
        "name" in room &&
        typeof room.name === "string" &&
        "capacity" in room &&
        Number.isInteger(room.capacity) &&
        "is_active" in room &&
        typeof room.is_active === "boolean",
    )
  ) {
    throw new Error("Dữ liệu danh sách phòng không đúng định dạng");
  }

  return payload as RoomsResponse;
}

export async function getRooms({
  signal,
}: RequestOptions = {}): Promise<RoomsResponse> {
  if (isMockEnabled()) {
    return parseRoomsResponse(MOCK_ROOMS);
  }

  const response = await fetch(
    new URL(`${API_BASE_URL}/rooms`, window.location.origin),
    { signal },
  );
  if (!response.ok) {
    throw new Error(`Rooms request failed (${response.status})`);
  }
  return parseRoomsResponse(await readJson(response));
}

export async function getCurrentOccupancy({
  signal,
  status,
  campus,
}: RequestOptions & { status?: MockOccupancyState; campus?: "CS1" | "CS3" } = {}): Promise<
  OccupancyResult | NormalizedOccupancy | null
> {
  if (isMockEnabled()) {
    const selectedState = getMockOccupancyState(status);
    const fixture = MOCK_OCCUPANCY[selectedState];
    const updatedAt =
      selectedState === "fresh" ? new Date().toISOString() : null;
    const snapshot = updatedAt
      ? {
          ...fixture,
          last_updated: updatedAt,
          rooms: fixture.rooms.map((room) => ({
            ...room,
            recorded_at: updatedAt,
            updated_at: updatedAt,
          })),
        }
      : fixture;
    const hasCompleteCounts =
      snapshot.rooms.length > 0 &&
      snapshot.rooms.every((room) => Number.isInteger(room.current_count));
    const summary = normalizeOccupancy({
      current_count: hasCompleteCounts
        ? snapshot.rooms.reduce(
            (total, room) => total + (room.current_count ?? 0),
            0,
          )
        : null,
      updated_at: snapshot.last_updated,
      location: `Cơ sở ${snapshot.campus}`,
    });

    return {
      ...snapshot,
      count: summary?.count ?? null,
      updatedAt: summary?.updatedAt ?? null,
      location: summary?.location ?? `Cơ sở ${snapshot.campus}`,
    };
  }

  const url = new URL(OCCUPANCY_ENDPOINT, window.location.origin);
  if (campus) url.searchParams.set("campus_code", campus);
  const response = await fetch(url, { signal });
  if (!response.ok) {
    throw new Error(`API trả về lỗi HTTP ${response.status}`);
  }

  return normalizeOccupancy(
    await readJson(response, "API không trả về JSON hợp lệ"),
  );
}

export function normalizeOccupancy(
  payload: unknown,
): NormalizedOccupancy | null {
  if (payload == null || (Array.isArray(payload) && payload.length === 0)) {
    return null;
  }
  if (typeof payload !== "object" || Array.isArray(payload)) {
    throw new Error("Dữ liệu API không đúng định dạng");
  }

  const wrapper = payload as Record<string, unknown>;
  const record =
    wrapper.data &&
    typeof wrapper.data === "object" &&
    !Array.isArray(wrapper.data)
      ? (wrapper.data as Record<string, unknown>)
      : wrapper;
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
  if (!Number.isInteger(count) || (count as number) < 0) {
    throw new Error("API trả về số người không hợp lệ");
  }

  const updatedAt =
    record.updated_at ??
    record.last_updated ??
    record.updatedAt ??
    record.timestamp ??
    null;

  return {
    count: count as number,
    updatedAt: typeof updatedAt === "string" ? updatedAt : null,
    location:
      typeof record.location === "string"
        ? record.location
        : typeof record.location_name === "string"
          ? record.location_name
          : null,
  };
}
