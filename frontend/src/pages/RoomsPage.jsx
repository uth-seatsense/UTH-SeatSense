import { useEffect, useState } from "react";
import { ApiError, getRoomOccupancy, getRooms } from "../services/api.js";
import { RoomCard } from "../components/RoomCard.tsx";

function occupancyForRoom(room, signal) {
  return getRoomOccupancy(room.id, { signal })
    .then((occupancy) => ({
      ...room,
      count: occupancy.estimated_occupancy,
      is_stale: occupancy.is_stale,
      updated_at: occupancy.recorded_at,
      error: ""
    }))
    .catch((error) => {
      if (error.name === "AbortError") throw error;
      if (error instanceof ApiError && error.status === 404) {
        return { ...room, count: null, is_stale: false, updated_at: null, error: "" };
      }
      return { ...room, count: null, is_stale: false, updated_at: null, error: error.message };
    });
}

export default function RoomsPage() {
  const [selectedCampus, setSelectedCampus] = useState("CS1");
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    async function loadRooms() {
      setLoading(true);
      setError("");
      try {
        const allRooms = await getRooms({ signal: controller.signal });
        const filteredRooms = allRooms.filter(
          (room) =>
            room.room_type === "free_area" &&
            room.campus_code === selectedCampus
        );
        const results = await Promise.all(
          filteredRooms.map((room) => occupancyForRoom(room, controller.signal)),
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
  }, [selectedCampus]);

  return (
    <main className="feature-page">
      <header className="feature-heading">
        <p className="eyebrow">Không gian thư viện</p>
        <h1>Tình trạng khu tự học</h1>
        <p>
          Số người và chỗ trống được cập nhật gần thời gian thực từ hệ thống đếm.
        </p>
      </header>

      <div className="campus-filter">
        <button
          className={`campus-tab ${selectedCampus === "CS1" ? "campus-tab--active" : ""}`}
          onClick={() => setSelectedCampus("CS1")}
          type="button"
        >
          Cơ sở 1
        </button>
        <button
          className={`campus-tab ${selectedCampus === "CS3" ? "campus-tab--active" : ""}`}
          onClick={() => setSelectedCampus("CS3")}
          type="button"
        >
          Cơ sở 3
        </button>
      </div>

      {loading && (
        <p className="loading-message" aria-live="polite">
          Đang tải dữ liệu mật độ...
        </p>
      )}

      {error && (
        <div className="feedback feedback--error" role="alert">
          Không thể tải dữ liệu: {error}
        </div>
      )}

      {!loading && !error && rooms.length === 0 && (
        <p className="empty-panel">
          Hiện chưa có khu tự học nào tại cơ sở này.
        </p>
      )}

      {!loading && !error && rooms.length > 0 && (
        <div className="room-grid">
          {rooms.map((room) => (
            <RoomCard
              key={room.id}
              room={room}
              capacity={room.capacity}
            />
          ))}
        </div>
      )}
    </main>
  );
}
