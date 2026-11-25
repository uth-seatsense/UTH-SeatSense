import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError, getRoomOccupancy, getRooms } from "../services/api.js";

function occupancyForRoom(room, signal) {
  return getRoomOccupancy(room.id, { signal })
    .then((occupancy) => ({ room, occupancy, error: "" }))
    .catch((error) => {
      if (error.name === "AbortError") throw error;
      if (error instanceof ApiError && error.status === 404) {
        return { room, occupancy: null, error: "" };
      }
      return { room, occupancy: null, error: error.message };
    });
}

export default function RoomsPage() {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    async function loadRooms() {
      setLoading(true);
      setError("");
      try {
        const activeRooms = await getRooms({ signal: controller.signal });
        const results = await Promise.all(
          activeRooms.map((room) => occupancyForRoom(room, controller.signal)),
        );
        if (active) setRooms(results);
      } catch (loadError) {
        if (active && loadError.name !== "AbortError") {
          setError(loadError.message);
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    loadRooms();
    return () => {
      active = false;
      controller.abort();
    };
  }, [reloadKey]);

  return (
    <main className="feature-page">
      <header className="feature-heading">
        <p className="eyebrow">Không gian thư viện</p>
        <h1>Tình trạng phòng</h1>
        <p>
          Số chỗ trống được tính từ sức chứa và số người ước tính gần nhất.
          Phòng chưa có dữ liệu sẽ không hiển thị như phòng còn trống.
        </p>
      </header>

      <div className="feature-toolbar">
        <span aria-live="polite">
          {loading
            ? "Đang tải danh sách phòng..."
            : `${rooms.length} phòng đang hoạt động`}
        </span>
        <button
          className="button button--secondary"
          disabled={loading}
          onClick={() => setReloadKey((value) => value + 1)}
          type="button"
        >
          Làm mới
        </button>
      </div>

      {error && (
        <div className="feedback feedback--error" role="alert">
          {error}
        </div>
      )}
      {!loading && !error && rooms.length === 0 && (
        <p className="empty-panel">Hiện chưa có phòng đang hoạt động.</p>
      )}
      <section aria-label="Danh sách phòng" className="room-grid">
        {rooms.map(({ room, occupancy, error: occupancyError }) => {
          const count = occupancy?.estimated_occupancy;
          const available =
            Number.isInteger(count) && count >= 0
              ? Math.max(0, room.capacity - count)
              : null;
          return (
            <article className="feature-panel room-card" key={room.id}>
              <div className="room-card__heading">
                <div>
                  <h2>{room.name}</h2>
                  <p>
                    {room.code}
                    {room.campus_code ? ` · ${room.campus_code}` : ""}
                  </p>
                </div>
                <span className="room-type">
                  {room.room_type === "topic_room"
                    ? "Phòng chuyên đề"
                    : "Khu tự học"}
                </span>
              </div>
              <p>Sức chứa: {room.capacity} người</p>
              <Link to={`/rooms/${room.id}`}>Xem chi tiết tình trạng</Link>
              {occupancyError ? (
                <p className="feedback feedback--error">
                  Không tải được số liệu: {occupancyError}
                </p>
              ) : available === null ? (
                <p className="data-unavailable">Chưa có dữ liệu chỗ trống.</p>
              ) : (
                <div className="room-availability">
                  <strong>{available}</strong>
                  <span>chỗ trống ước tính</span>
                  {count > room.capacity ? (
                    <span className="feedback feedback--warning">
                      ⚠ Vượt sức chứa
                    </span>
                  ) : null}
                  {occupancy.is_stale && (
                    <span className="feedback feedback--warning">
                      Dữ liệu đã cũ, hãy kiểm tra lại trước khi sử dụng.
                    </span>
                  )}
                </div>
              )}
              {room.room_type === "topic_room" && (
                <Link
                  className="button button--primary"
                  to={`/reservation?room=${room.id}`}
                >
                  Đặt phòng
                </Link>
              )}
            </article>
          );
        })}
      </section>
    </main>
  );
}
