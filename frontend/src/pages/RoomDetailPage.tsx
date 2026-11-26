import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  OccupancyBadge,
  getOccupancyLevel,
} from "../components/OccupancyBadge";
import StaleWarning from "../components/StaleWarning";
import { useOccupancyPolling } from "../hooks/useOccupancyPolling";
import {
  getRoomDetails,
  getRoomOccupancyDetail,
  type RoomDetailSnapshot,
  type RoomOccupancyDetail,
} from "../services/roomApi";

type StaleStatus = "stale" | "disconnected" | "insufficient";

function formatUpdatedAt(value: string | null): string | null {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return new Intl.DateTimeFormat("vi-VN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function getStaleStatus(
  room: RoomDetailSnapshot,
  occupancy: RoomOccupancyDetail | null,
  error: string,
): StaleStatus | null {
  if (error) return "disconnected";
  if (!occupancy) return "insufficient";
  if (
    occupancy.device_status === "offline" ||
    occupancy.device_status === "error" ||
    occupancy.occupancy_status === "offline"
  ) {
    return "disconnected";
  }
  if (occupancy.is_stale || occupancy.occupancy_status === "stale") {
    return "stale";
  }
  if (
    !Number.isInteger(room.capacity) ||
    room.capacity <= 0 ||
    room.capacity_confirmed === false ||
    occupancy.estimated_occupancy === null ||
    occupancy.occupancy_status === "insufficient"
  ) {
    return "insufficient";
  }
  return null;
}

function RoomOccupancyView({ room }: { room: RoomDetailSnapshot }) {
  const fetchSnapshot = useCallback(
    (signal: AbortSignal) => getRoomOccupancyDetail(room.id, { signal }),
    [room.id],
  );
  const { data, isLoading, isRefreshing, error } =
    useOccupancyPolling(fetchSnapshot);
  const status = getStaleStatus(room, data, error);
  const updatedAt = data?.recorded_at ?? data?.received_at ?? null;
  const formattedUpdatedAt = formatUpdatedAt(updatedAt);
  const count = data?.estimated_occupancy;
  const metrics =
    status === null && count !== null && count !== undefined
      ? {
          count,
          availableSeats: Math.max(0, room.capacity - count),
          overCapacity: count > room.capacity,
        }
      : null;

  return (
    <main className="feature-page room-detail-page">
      <header className="feature-heading">
        <p className="eyebrow">Tình trạng khu tự học</p>
        <h1>{room.name}</h1>
        <p>
          {room.code}
          {room.campus_code ? ` · ${room.campus_code}` : ""}
        </p>
      </header>

      <p className="room-detail-refresh" aria-live="polite">
        {isLoading
          ? "Đang tải số liệu..."
          : isRefreshing
            ? "Đang cập nhật số liệu..."
            : "Tự động cập nhật mỗi 3–5 giây"}
      </p>

      {status && <StaleWarning status={status} lastUpdatedAt={updatedAt} />}
      {error && (
        <p className="feedback feedback--error" role="alert">
          Không thể cập nhật số liệu: {error}
        </p>
      )}

      {metrics && (
        <section
          className="feature-panel room-detail-metrics"
          aria-label="Số liệu mật độ phòng"
        >
          <div className="room-detail-metric">
            <span>Số người hiện tại</span>
            <strong>{metrics.count} người</strong>
          </div>
          <div className="room-detail-metric">
            <span>Sức chứa</span>
            <strong>{room.capacity} người</strong>
          </div>
          <div className="room-detail-metric">
            <span>Chỗ trống</span>
            <strong>{metrics.availableSeats} chỗ</strong>
          </div>
          <div className="room-detail-metric">
            <span>Mức độ đông</span>
            <div className="room-detail-density">
              <OccupancyBadge
                level={getOccupancyLevel(metrics.count, room.capacity)}
              />
              <span>
                {Math.round((metrics.count / room.capacity) * 100)}% sức chứa
              </span>
            </div>
          </div>
          {metrics.overCapacity && (
            <p className="room-detail-over-capacity" role="alert">
              Vượt sức chứa ({metrics.count} người trên {room.capacity} người).
              Chỗ trống được hiển thị là 0.
            </p>
          )}
          <p className="room-detail-updated">
            Cập nhật lần cuối:{" "}
            {formattedUpdatedAt ? (
              <time dateTime={updatedAt ?? undefined}>
                {formattedUpdatedAt}
              </time>
            ) : (
              "chưa có thời điểm"
            )}
          </p>
        </section>
      )}

      <Link className="room-detail-back" to="/rooms">
        Quay lại danh sách phòng
      </Link>
    </main>
  );
}

function RoomDetailContent({ roomId }: { roomId: number }) {
  const [room, setRoom] = useState<RoomDetailSnapshot | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    getRoomDetails(roomId, { signal: controller.signal })
      .then((result) => {
        if (active) setRoom(result);
      })
      .catch((loadError: unknown) => {
        if (
          active &&
          !(loadError instanceof Error && loadError.name === "AbortError")
        ) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : "Không thể tải thông tin phòng.",
          );
        }
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });

    return () => {
      active = false;
      controller.abort();
    };
  }, [roomId]);

  if (isLoading) {
    return (
      <main className="feature-page room-detail-page" aria-live="polite">
        <p>Đang tải thông tin phòng...</p>
      </main>
    );
  }

  if (error || !room) {
    return (
      <main className="feature-page room-detail-page">
        <p className="feedback feedback--error" role="alert">
          {error || "Không tìm thấy phòng."}
        </p>
        <Link to="/rooms">Quay lại danh sách phòng</Link>
      </main>
    );
  }

  return <RoomOccupancyView room={room} />;
}

export default function RoomDetailPage() {
  const { roomId: rawRoomId } = useParams();
  const roomId = Number(rawRoomId);

  if (!Number.isSafeInteger(roomId) || roomId <= 0) {
    return (
      <main className="feature-page room-detail-page">
        <p className="feedback feedback--error" role="alert">
          Mã phòng không hợp lệ.
        </p>
        <Link to="/rooms">Quay lại danh sách phòng</Link>
      </main>
    );
  }

  return <RoomDetailContent key={roomId} roomId={roomId} />;
}
