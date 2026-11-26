import {
  ApiError,
  getCurrentOccupancy,
  getRoomById,
  getRoomOccupancy,
  getRooms,
  isMockEnabled,
} from "./api.js";

export type CampusCode = "CS1" | "CS3";

export interface RoomSnapshot {
  id: number;
  code: string;
  name: string;
  room_type: string;
  capacity: number;
  campus_code: string | null;
  is_active: boolean;
}

export interface RoomDetailSnapshot extends RoomSnapshot {
  building: string | null;
  capacity_confirmed?: boolean;
}

export interface RoomOccupancyDetail {
  estimated_occupancy: number | null;
  recorded_at: string | null;
  received_at: string | null;
  is_stale: boolean;
  device_status?: "online" | "offline" | "error";
  occupancy_status?: "fresh" | "stale" | "offline" | "insufficient";
}

export interface RoomOccupancySnapshot extends RoomSnapshot {
  count: number | null;
  updated_at: string | null;
  is_stale: boolean;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function parseRoomSnapshot(value: unknown): RoomDetailSnapshot {
  if (
    !isRecord(value) ||
    !Number.isInteger(value.id) ||
    typeof value.code !== "string" ||
    typeof value.name !== "string" ||
    typeof value.room_type !== "string" ||
    !Number.isInteger(value.capacity) ||
    typeof value.is_active !== "boolean" ||
    (value.campus_code !== null && typeof value.campus_code !== "string") ||
    (value.building !== null && typeof value.building !== "string") ||
    ("capacity_confirmed" in value &&
      typeof value.capacity_confirmed !== "boolean")
  ) {
    throw new Error("Dữ liệu phòng không đúng định dạng.");
  }

  return {
    id: value.id as number,
    code: value.code,
    name: value.name,
    room_type: value.room_type,
    capacity: value.capacity as number,
    campus_code: value.campus_code,
    building: value.building,
    is_active: value.is_active,
    ...(typeof value.capacity_confirmed === "boolean"
      ? { capacity_confirmed: value.capacity_confirmed }
      : {}),
  };
}

function parseOccupancyDetail(value: unknown): RoomOccupancyDetail {
  if (!isRecord(value)) {
    throw new Error("Dữ liệu mật độ phòng không đúng định dạng.");
  }

  const rawCount =
    "estimated_occupancy" in value
      ? value.estimated_occupancy
      : value.current_count;
  if (
    rawCount === undefined ||
    (rawCount !== null &&
      (!Number.isInteger(rawCount) || (rawCount as number) < 0))
  ) {
    throw new Error("Số người trong dữ liệu mật độ không hợp lệ.");
  }

  const recordedAt = value.recorded_at ?? value.updated_at ?? null;
  const receivedAt = value.received_at ?? value.last_updated ?? null;
  const deviceStatus = value.device_status;
  if (
    deviceStatus !== undefined &&
    deviceStatus !== "online" &&
    deviceStatus !== "offline" &&
    deviceStatus !== "error"
  ) {
    throw new Error("Trạng thái nguồn đếm không hợp lệ.");
  }

  const occupancyStatus = value.occupancy_status;
  if (
    occupancyStatus !== undefined &&
    occupancyStatus !== "fresh" &&
    occupancyStatus !== "stale" &&
    occupancyStatus !== "offline" &&
    occupancyStatus !== "insufficient"
  ) {
    throw new Error("Trạng thái mật độ không hợp lệ.");
  }

  if (
    (recordedAt !== null && typeof recordedAt !== "string") ||
    (receivedAt !== null && typeof receivedAt !== "string") ||
    (value.is_stale !== undefined && typeof value.is_stale !== "boolean") ||
    (value.is_stale === undefined && occupancyStatus === undefined)
  ) {
    throw new Error("Trạng thái cập nhật mật độ không đúng định dạng.");
  }

  return {
    estimated_occupancy: rawCount as number | null,
    recorded_at: recordedAt,
    received_at: receivedAt,
    is_stale: value.is_stale === true || occupancyStatus === "stale",
    ...(deviceStatus ? { device_status: deviceStatus } : {}),
    ...(occupancyStatus ? { occupancy_status: occupancyStatus } : {}),
  };
}

export async function getRoomDetails(
  roomId: number,
  options: { signal?: AbortSignal } = {},
): Promise<RoomDetailSnapshot> {
  if (!Number.isInteger(roomId) || roomId <= 0) {
    throw new Error("Mã phòng không hợp lệ.");
  }

  const response: unknown = await getRoomById(roomId, {
    signal: options.signal,
  });
  if (response === undefined) {
    throw new Error("Không tìm thấy phòng.");
  }

  return parseRoomSnapshot(response);
}

export async function getRoomOccupancyDetail(
  roomId: number,
  options: { signal?: AbortSignal } = {},
): Promise<RoomOccupancyDetail> {
  let response: unknown;
  try {
    response = isMockEnabled()
      ? await getCurrentOccupancy({ signal: options.signal })
      : await getRoomOccupancy(roomId, { signal: options.signal });
  } catch (error) {
    if (
      error instanceof ApiError &&
      (error.code === "occupancy_not_found" ||
        error.code === "occupancy_unavailable")
    ) {
      return {
        estimated_occupancy: null,
        recorded_at: null,
        received_at: null,
        is_stale: false,
        occupancy_status: "insufficient",
      };
    }
    throw error;
  }

  if (isMockEnabled() && isRecord(response) && Array.isArray(response.rooms)) {
    const roomOccupancy = response.rooms.find(
      (room: unknown) => isRecord(room) && room.room_id === roomId,
    );
    if (roomOccupancy === undefined) {
      return {
        estimated_occupancy: null,
        recorded_at: null,
        received_at: null,
        is_stale: false,
        occupancy_status: "insufficient",
      };
    }
    return parseOccupancyDetail(roomOccupancy);
  }

  return parseOccupancyDetail(response);
}

export async function getCampusRooms(
  campusCode: CampusCode,
  options: { signal?: AbortSignal } = {},
): Promise<RoomOccupancySnapshot[]> {
  const response = await getRooms({ signal: options.signal });
  const rooms = [...response.items].filter(
    (room: RoomSnapshot) =>
      room.is_active && (room.campus_code ?? "").toUpperCase() === campusCode,
  ) as RoomSnapshot[];

  if (isMockEnabled()) {
    return rooms.map((room) => ({
      ...room,
      count: 10,
      updated_at: new Date().toISOString(),
      is_stale: false,
    }));
  }

  const results = await Promise.all(
    rooms.map(async (room) => {
      try {
        const occupancy = await getRoomOccupancy(room.id, {
          signal: options.signal,
        });
        return {
          ...room,
          count: Number.isInteger(occupancy.estimated_occupancy)
            ? occupancy.estimated_occupancy
            : null,
          updated_at: occupancy.recorded_at ?? occupancy.received_at ?? null,
          is_stale: Boolean(occupancy.is_stale),
        };
      } catch (error) {
        if ((error as { name?: string }).name === "AbortError") throw error;
        return {
          ...room,
          count: null,
          updated_at: null,
          is_stale: false,
        };
      }
    }),
  );

  return results;
}
