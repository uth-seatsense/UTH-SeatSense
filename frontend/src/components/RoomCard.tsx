import { OccupancyBadge, getOccupancyLevel } from "./OccupancyBadge";
import type { RoomOccupancySnapshot } from "../services/roomApi";

export interface RoomCardProps {
  room: RoomOccupancySnapshot;
  capacity: number;
}

export function RoomCard({ room, capacity }: RoomCardProps) {
  const count = room.count;
  const hasData = count !== null && count !== undefined;
  const occupancyPercent = hasData && capacity > 0
    ? Math.round((count / capacity) * 100)
    : null;
  const level = hasData && capacity > 0
    ? getOccupancyLevel(count, capacity)
    : null;

  return (
    <article
      className="room-card"
      aria-label={`${room.name}: ${hasData ? `${count} người` : "chưa có dữ liệu"}`}
    >
      <div className="room-card__header">
        <div>
          <h3 className="room-card__name">{room.name}</h3>
          <p className="room-card__meta">
            {room.code}
            {room.campus_code ? ` · ${room.campus_code}` : ""}
          </p>
        </div>
        {level && <OccupancyBadge level={level} />}
      </div>

      {hasData ? (
        <div className="room-card__occupancy">
          <div className="room-card__count">
            <strong>{count}</strong>
            <span> / {capacity}</span>
          </div>
          {occupancyPercent !== null && (
            <div className="room-card__percent">{occupancyPercent}%</div>
          )}
        </div>
      ) : (
        <div className="room-card__empty">Chưa có dữ liệu</div>
      )}

      {room.is_stale && hasData && (
        <p className="room-card__warning">Dữ liệu đã cũ</p>
      )}
    </article>
  );
}

export default RoomCard;
