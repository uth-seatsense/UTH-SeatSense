import type { RoomOccupancySnapshot } from "../services/roomApi";

export interface RoomCardProps {
  room: RoomOccupancySnapshot;
}

export function RoomCard({ room }: RoomCardProps) {
  return (
    <article className="dashboard-room-card" aria-label={`${room.name}: ${room.count ?? "chưa có dữ liệu"} người`}>
      <h3>{room.name}</h3>
      {room.count === null ? (
        <strong className="dashboard-room-card__empty">Chưa có dữ liệu</strong>
      ) : (
        <strong className="dashboard-room-card__count">
          {room.count}
          <span>người</span>
        </strong>
      )}
    </article>
  );
}

export default RoomCard;
