import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { createBooking, getRooms } from "../services/api.js";

function toLocalDateTimeValue(date) {
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
  return local.toISOString().slice(0, 16);
}

function localDateTimeToIso(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    throw new Error("Vui lòng nhập ngày giờ hợp lệ.");
  }
  return date.toISOString();
}

export default function ReservationPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [rooms, setRooms] = useState([]);
  const [loadingRooms, setLoadingRooms] = useState(true);
  const [roomsError, setRoomsError] = useState("");
  const [roomId, setRoomId] = useState(searchParams.get("room") ?? "");
  const [startsAt, setStartsAt] = useState(() => {
    const start = new Date();
    start.setMinutes(0, 0, 0);
    start.setHours(start.getHours() + 2);
    return toLocalDateTimeValue(start);
  });
  const [endsAt, setEndsAt] = useState(() => {
    const end = new Date();
    end.setMinutes(0, 0, 0);
    end.setHours(end.getHours() + 3);
    return toLocalDateTimeValue(end);
  });
  const [participantCount, setParticipantCount] = useState(2);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    getRooms({ signal: controller.signal })
      .then((items) => {
        setRooms(items.filter((room) => room.room_type === "topic_room"));
        setRoomsError("");
      })
      .catch((loadError) => {
        if (loadError.name !== "AbortError") setRoomsError(loadError.message);
      })
      .finally(() => setLoadingRooms(false));
    return () => controller.abort();
  }, []);

  const selectedRoom = useMemo(
    () => rooms.find((room) => String(room.id) === roomId),
    [rooms, roomId],
  );

  async function submitBooking(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await createBooking({
        roomId: Number(roomId),
        startsAt: localDateTimeToIso(startsAt),
        endsAt: localDateTimeToIso(endsAt),
        participantCount: Number(participantCount),
      });
      navigate("/my-bookings", {
        state: { notice: "Đặt phòng thành công." },
      });
    } catch (bookingError) {
      setError(bookingError.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="feature-page feature-page--narrow">
      <header className="feature-heading">
        <p className="eyebrow">Đặt chỗ nhóm</p>
        <h1>Đặt phòng chuyên đề</h1>
        <p>
          Chọn thời gian theo giờ địa phương của thiết bị. Hệ thống sẽ kiểm tra
          giới hạn và xung đột trước khi xác nhận.
        </p>
      </header>

      {roomsError && (
        <p className="feedback feedback--error" role="alert">
          Không tải được danh sách phòng: {roomsError}
        </p>
      )}
      {!loadingRooms && !roomsError && rooms.length === 0 && (
        <p className="empty-panel">Hiện chưa có phòng chuyên đề để đặt.</p>
      )}

      <form className="feature-panel feature-form" onSubmit={submitBooking}>
        <label className="form-field">
          <span>Phòng</span>
          <select
            disabled={loadingRooms || rooms.length === 0 || busy}
            onChange={(event) => setRoomId(event.target.value)}
            required
            value={roomId}
          >
            <option value="">Chọn phòng</option>
            {rooms.map((room) => (
              <option key={room.id} value={room.id}>
                {room.name} ({room.code}) · sức chứa {room.capacity}
              </option>
            ))}
          </select>
        </label>
        {selectedRoom && (
          <p className="helper-text">
            {selectedRoom.campus_code || "Chưa gán cơ sở"}
            {selectedRoom.building ? ` · ${selectedRoom.building}` : ""}
          </p>
        )}
        <div className="form-row">
          <label className="form-field">
            <span>Bắt đầu</span>
            <input
              disabled={busy}
              onChange={(event) => setStartsAt(event.target.value)}
              required
              type="datetime-local"
              value={startsAt}
            />
          </label>
          <label className="form-field">
            <span>Kết thúc</span>
            <input
              disabled={busy}
              onChange={(event) => setEndsAt(event.target.value)}
              required
              type="datetime-local"
              value={endsAt}
            />
          </label>
        </div>
        <label className="form-field">
          <span>Số thành viên (2–6)</span>
          <input
            disabled={busy}
            max={6}
            min={2}
            onChange={(event) => setParticipantCount(event.target.value)}
            required
            type="number"
            value={participantCount}
          />
        </label>
        <p className="helper-text">
          Thời lượng và thời gian đặt trước áp dụng theo quy định hiện tại của
          Backend.
        </p>
        {error && (
          <p className="feedback feedback--error" role="alert">
            {error}
          </p>
        )}
        <button
          className="button button--primary"
          disabled={busy || loadingRooms || rooms.length === 0}
          type="submit"
        >
          {busy ? "Đang xác nhận..." : "Xác nhận đặt phòng"}
        </button>
      </form>
    </main>
  );
}
