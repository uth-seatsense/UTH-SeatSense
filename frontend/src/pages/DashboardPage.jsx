import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  getCurrentOccupancy,
  getRoomOccupancyStatus,
  isMockEnabled,
} from "../services/api.js";

const REFRESH_INTERVAL = 30_000;
const CAMPUS_LABELS = {
  cs1: "Cơ sở 1 (Võ Oanh - B.301A)",
  cs3: "Cơ sở 3 (Tòa K - Lầu 2)",
};

const areas = [
  {
    name: "B301A - Lầu 1",
    category: "Tự học & Máy tính",
    description: "Bàn rộng, có sẵn các tiện ích học tập",
  },
  {
    name: "B301A - Lầu 2",
    category: "Đọc sách yên tĩnh",
    description: "Không gian nghiên cứu và đọc tài liệu",
  },
  {
    name: "Phòng Chuyên Đề 1",
    category: "Học nhóm",
    description: "Không gian học tập theo nhóm",
  },
  {
    name: "Phòng Chuyên Đề 2",
    category: "Học nhóm",
    description: "Không gian học tập theo nhóm",
  },
];

function formatUpdatedAt(value) {
  if (!value) {
    return null;
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("vi-VN", {
    dateStyle: "short",
    timeStyle: "medium",
  }).format(date);
}

function Icon({ children, className = "" }) {
  return (
    <span className={`material-symbols-outlined ${className}`} aria-hidden="true">
      {children}
    </span>
  );
}

function Sidebar() {
  return (
    <aside className="sidebar">
      <div>
        <a className="brand" href="#dashboard">
          <span className="brand-mark">
            <Icon>school</Icon>
          </span>
          <span className="brand-copy">
            <strong>UTH-SeatSense</strong>
            <small>Đại học Giao thông Vận tải TP.HCM</small>
          </span>
        </a>
        <nav className="side-nav" aria-label="Điều hướng chính">
          <a className="side-link active" href="#dashboard" aria-current="page">
            <Icon>dashboard</Icon>
            Tổng quan
          </a>
          <Link className="side-link" to="/reservation">
            <Icon>meeting_room</Icon>
            Đặt phòng học
          </Link>
        </nav>
      </div>
      <nav className="side-nav sidebar-footer" aria-label="Thông tin">
        <a className="side-link" href="#help">
          <Icon>help_outline</Icon>
          Hỗ trợ &amp; Hướng dẫn
        </a>
        <a className="side-link" href="#settings">
          <Icon>settings</Icon>
          Cài đặt hệ thống
        </a>
      </nav>
    </aside>
  );
}

function MetricCard({ label, value, unit, icon, variant, note, children }) {
  return (
    <section className="metric-card">
      <div className="metric-heading">
        <span>{label}</span>
        <Icon className={variant}>{icon}</Icon>
      </div>
      <div className={`metric-value ${variant || ""}`}>
        {value}
        {unit && <span className="metric-unit">{unit}</span>}
      </div>
      {children || <p className="metric-note">{note}</p>}
    </section>
  );
}

function AreaRow({ area, isLoading }) {
  return (
    <article className="area-row">
      <div className="area-description">
        <div className="area-name-line">
          <strong>{area.name}</strong>
          <span className="area-tag">{area.category}</span>
        </div>
        <p>{area.description}</p>
      </div>
      <div className="area-stat">
        <div className="area-count">
          <strong>
            {isLoading
              ? "Đang tải"
              : area.current_count != null
                ? `${area.current_count} người`
                : "Chưa có dữ liệu"}
          </strong>
          <span>
            {area.available_seats != null
              ? `${area.available_seats} chỗ trống`
              : "—"}
          </span>
        </div>
        <div className="area-track" aria-hidden="true">
          <span />
        </div>
      </div>
      <span className="area-status">
        {isLoading
          ? "Đang tải"
          : area.is_stale
            ? "Dữ liệu cũ"
            : "Cập nhật trực tiếp"}
      </span>
    </article>
  );
}

export function getOccupancyConnectionStatus({ error, isLoading, occupancy }) {
  if (error) {
    return { text: "Không thể cập nhật", className: "error" };
  }
  if (isLoading) {
    return { text: "Đang tải dữ liệu", className: "loading" };
  }
  if (!occupancy) {
    return { text: "Chưa có dữ liệu", className: "empty" };
  }
  if (occupancy.device_status === "offline") {
    return { text: "Nguồn mất kết nối", className: "error" };
  }
  if (occupancy.is_stale) {
    return { text: "Dữ liệu đã cũ", className: "stale" };
  }
  return { text: "Cập nhật trực tiếp", className: "" };
}

export default function DashboardPage() {
  const [occupancy, setOccupancy] = useState(null);
  const [roomOccupancyStatus, setRoomOccupancyStatus] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [campus, setCampus] = useState("cs1");
  const hasLoadedRef = useRef(false);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    let timeoutId;

    async function loadOccupancy() {
      setError("");
      setIsLoading(!hasLoadedRef.current);
      setIsRefreshing(hasLoadedRef.current);

      try {
        const [result, roomStatus] = await Promise.all([
          getCurrentOccupancy({
            signal: controller.signal,
            campus: campus === "cs1" ? "CS1" : "CS3",
          }),
          getRoomOccupancyStatus({
            signal: controller.signal,
            campus: campus === "cs1" ? "CS1" : "CS3",
          }),
        ]);
        if (active) {
          setOccupancy(result);
          setRoomOccupancyStatus(roomStatus);
        }
      } catch (requestError) {
        if (active && requestError.name !== "AbortError") {
          setError(requestError.message || "Không thể kết nối đến máy chủ.");
        }
      } finally {
        if (active) {
          hasLoadedRef.current = true;
          setIsLoading(false);
          setIsRefreshing(false);
          timeoutId = window.setTimeout(loadOccupancy, REFRESH_INTERVAL);
        }
      }
    }

    loadOccupancy();

    return () => {
      active = false;
      controller.abort();
      window.clearTimeout(timeoutId);
    };
  }, [campus, refreshKey]);

  const updatedAt = formatUpdatedAt(occupancy?.updatedAt);
  const connectionStatus = getOccupancyConnectionStatus({
    error,
    isLoading,
    occupancy,
  });
  const displayCount = occupancy?.count != null
    ? new Intl.NumberFormat("vi-VN").format(occupancy.count)
    : "—";
  const countValue = displayCount;
  const roomStatus = roomOccupancyStatus;
  const totalCapacity = roomStatus?.rooms?.reduce(
    (total, room) => total + room.capacity,
    0,
  ) ?? null;
  const totalAvailable = roomStatus?.rooms?.reduce(
    (total, room) => total + (room.available_seats ?? 0),
    0,
  ) ?? null;
  const webLoggedCount = roomStatus?.web_logged_in_count;
  const location = occupancy?.location || "Thư viện UTH";
  const campusLabel = CAMPUS_LABELS[campus];
  const dataSourceNote = isRefreshing
    ? "Đang làm mới dữ liệu"
    : isMockEnabled()
      ? "Dữ liệu mô phỏng (mock)"
      : "Dữ liệu từ Backend API";

  return (
    <div className="app-shell" id="dashboard">
      <Sidebar />
      <header className="topbar">
        <div className="topbar-tools">
          <label className="search-box">
            <Icon>search</Icon>
            <input
              type="search"
              placeholder="Tìm tầng, phòng, bàn học hoặc vị trí..."
              aria-label="Tìm tầng, phòng, bàn học hoặc vị trí"
            />
          </label>
          <button type="button" className="map-button">
            <Icon>map</Icon>
            <span>Sơ đồ trường</span>
          </button>
        </div>
        <div className="topbar-actions">
          <button type="button" className="checkin-button" disabled>
            <Icon>qr_code_scanner</Icon>
            <span>Check-in QR</span>
          </button>
          <button
            type="button"
            className="icon-button notification-button"
            title="Thông báo hệ thống"
            aria-label="Thông báo hệ thống"
          >
            <Icon>notifications</Icon>
          </button>
          <span className="topbar-divider" />
          <div className="profile">
            <span className="profile-avatar">
              <Icon>person</Icon>
            </span>
            <span className="profile-copy">
              <strong>Sinh viên UTH</strong>
              <small>Tài khoản</small>
            </span>
          </div>
        </div>
      </header>

      <main className="main-content">
        <div className="page-heading">
          <div className="heading-title">
            <h1>Tổng quan Thư viện UTH</h1>
            <span
              className={`connection-pill ${connectionStatus.className}`}
              role="status"
            >
              <span className="status-dot" />
              {updatedAt && connectionStatus.className === ""
                  ? `Cập nhật: ${updatedAt}`
                  : connectionStatus.text}
            </span>
          </div>
          <div className="campus-switcher" role="group" aria-label="Chọn cơ sở">
            <button
              type="button"
              className={campus === "cs1" ? "selected" : ""}
              aria-pressed={campus === "cs1"}
              onClick={() => setCampus("cs1")}
            >
              <Icon>domain</Icon>
              {CAMPUS_LABELS.cs1}
            </button>
            <button
              type="button"
              className={campus === "cs3" ? "selected" : ""}
              aria-pressed={campus === "cs3"}
              onClick={() => setCampus("cs3")}
            >
              <Icon>location_city</Icon>
              {CAMPUS_LABELS.cs3}
            </button>
          </div>
        </div>

        {error && (
          <div className="alert" role="alert">
            <Icon>error</Icon>
            <div className="alert-content">
              <strong>Không thể cập nhật dữ liệu</strong>
              <span>
                {error}
                {occupancy &&
                  " Đang hiển thị số liệu đã tải thành công gần nhất."}
              </span>
            </div>
            <button
              className="retry-button"
              type="button"
              onClick={() => setRefreshKey((key) => key + 1)}
            >
              <Icon>refresh</Icon>
              Thử lại
            </button>
          </div>
        )}

        {!isLoading && !error && !occupancy && (
          <div className="empty-state" role="status">
            <Icon>info</Icon>
            <span>Chưa có dữ liệu số người hiện tại từ hệ thống.</span>
          </div>
        )}

        <section className="metrics-grid" aria-label="Thống kê thư viện">
          <MetricCard
            label="Sức chứa"
            value={totalCapacity != null ? new Intl.NumberFormat("vi-VN").format(totalCapacity) : "—"}
            unit="chỗ"
            icon="chair_alt"
            variant="primary"
            note={totalCapacity != null ? "Tổng sức chứa phòng đang hoạt động" : "Chưa có dữ liệu sức chứa"}
          />
          <MetricCard
            label="Đang có mặt"
            value={countValue}
            unit="người"
            icon="group"
            variant="secondary"
            note={dataSourceNote}
          />
          <MetricCard
            label="Còn trống"
            value={totalAvailable != null ? new Intl.NumberFormat("vi-VN").format(totalAvailable) : "—"}
            unit="chỗ trống"
            icon="event_seat"
            variant="green"
            note={totalAvailable != null ? "Tính từ số người mới nhất từng phòng" : "Chưa có dữ liệu sức chứa"}
          />
          <MetricCard
            label="Đang đăng nhập Web"
            value={webLoggedCount != null ? new Intl.NumberFormat("vi-VN").format(webLoggedCount) : "—"}
            unit="người"
            icon="person"
            variant="secondary"
            note="Phiên đăng nhập còn hiệu lực"
          />
          <MetricCard
            label="Mật độ trung bình"
            value="—"
            unit=""
            icon="speed"
            variant="primary"
          >
            <div className="metric-progress">
              <span />
            </div>
          </MetricCard>
        </section>

        <div className="content-grid">
          <section className="panel areas-panel">
            <div className="section-heading">
              <div>
                <Icon>analytics</Icon>
                <h2>Mật độ các khu vực — {campusLabel}</h2>
              </div>
            </div>
            <div className="area-list">
              {roomOccupancyStatus?.rooms?.length
                ? roomOccupancyStatus.rooms.map((room) => (
                    <AreaRow
                      key={room.room_id}
                      area={{
                        name: room.room_name,
                        category: room.room_code,
                        description: `Sức chứa ${room.capacity} người`,
                        current_count: room.current_count,
                        available_seats: room.available_seats,
                        is_stale: room.is_stale,
                      }}
                      isLoading={isLoading}
                    />
                  ))
                : areas.map((area) => (
                    <AreaRow key={area.name} area={area} isLoading={isLoading} />
                  ))}
            </div>
            {!isLoading && !error && (
              <p className="panel-footnote">
                Số người và chỗ trống được lấy từ bản ghi mới nhất từng phòng.
                Dữ liệu cũ hơn 30 giây được đánh dấu là stale.
              </p>
            )}
          </section>

          <aside className="right-column">
            <section className="panel booking-panel">
              <div className="section-heading compact">
                <div>
                  <Icon>event_available</Icon>
                  <h2>Lịch đặt phòng sắp tới</h2>
                </div>
                <span className="small-badge">Chưa kết nối</span>
              </div>
              <div className="booking-empty">
                <Icon>event_busy</Icon>
                <p>Lịch đặt phòng sẽ hiển thị khi có dữ liệu từ hệ thống.</p>
              </div>
              <button type="button" className="qr-button" disabled>
                <Icon>qr_code_scanner</Icon>
                Xem mã QR Check-in
              </button>
            </section>

            <section className="panel notice-panel">
              <div className="section-heading compact">
                <div>
                  <Icon>campaign</Icon>
                  <h2>Thông báo thư viện</h2>
                </div>
                <span className="muted-label">Mới nhất</span>
              </div>
              <div className="notice-empty">
                Thông báo sẽ hiển thị tại đây khi được cung cấp bởi hệ thống.
              </div>
            </section>
          </aside>
        </div>

        <p className="footer-note">
          UTH-SeatSense · {location} · Dữ liệu được cung cấp bởi hệ thống
        </p>
      </main>
    </div>
  );
}
