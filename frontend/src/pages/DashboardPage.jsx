import { useCallback, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { getCurrentOccupancy, isMockEnabled } from "../services/api.js";
import { getCampusRooms } from "../services/roomApi.ts";
import { useOccupancyPolling } from "../hooks/useOccupancyPolling.ts";
import RoomCard from "../components/RoomCard.tsx";
import { StaleWarning } from "../components/StaleWarning.tsx";

const CAMPUS_LABELS = {
  cs1: "Cơ sở 1 (Võ Oanh - B.301A)",
  cs3: "Cơ sở 3 (Tòa K - Lầu 2)",
};

const areas = [
  {
    name: "B301A - Lầu 1",
    category: "Tự học & Máy tính",
    description: "Bàn rộng, có sẵn các tiện ích học tập",
    current: "48",
    total: "120",
    percent: "40",
    status: "Thoáng",
    tone: "empty",
  },
  {
    name: "B301A - Lầu 2",
    category: "Đọc sách yên tĩnh",
    description: "Không gian nghiên cứu và đọc tài liệu",
    current: "26",
    total: "80",
    percent: "32",
    status: "Rất thoáng",
    tone: "empty",
  },
  {
    name: "Phòng Chuyên Đề 1",
    category: "Học nhóm",
    description: "Không gian học tập theo nhóm",
    current: "6",
    total: "12",
    percent: "50",
    status: "Đang dùng",
    tone: "medium",
  },
  {
    name: "Phòng Chuyên Đề 2",
    category: "Học nhóm",
    description: "Không gian học tập theo nhóm",
    current: "0",
    total: "10",
    percent: "0",
    status: "Trống",
    tone: "empty",
  },
];

const cs3Areas = [
  {
    name: "Toàn sàn tự học mở Tầng 1 (Tòa K)",
    category: "Tòa K",
    description: "Bàn tự học; khu vực mở, thoáng, không chia phòng.",
    current: "48",
    total: "120",
    percent: "40",
    status: "Thoáng",
    tone: "empty",
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
  const { pathname } = useLocation();
  const path = pathname.replace(/\/+$/, "") || "/";

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
          <Link
            className={`side-link ${path === "/" || path === "/dashboard" ? "active" : ""}`}
            to="/dashboard"
            aria-current={path === "/" || path === "/dashboard" ? "page" : undefined}
          >
            <Icon>dashboard</Icon>
            Tổng quan
          </Link>
          <Link className="side-link" to="/reservation">
            <Icon>meeting_room</Icon>
            Đặt phòng học
          </Link>
          <Link
            className={`side-link ${path === "/my-bookings" ? "active" : ""}`}
            to="/my-bookings"
            aria-current={path === "/my-bookings" ? "page" : undefined}
          >
            <Icon>history</Icon>
            Lịch đặt
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
          <strong>{isLoading ? "Đang tải" : `${area.current} / ${area.total}`}</strong>
          <span>{area.percent}%</span>
        </div>
        <div className="area-track" aria-hidden="true">
          <span className={`area-track-fill ${area.tone}`} style={{ width: `${area.percent}%` }} />
        </div>
      </div>
      <span className={`area-status ${area.tone}`}>
        {isLoading ? "Đang tải" : area.status}
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
  const [refreshKey, setRefreshKey] = useState(0);
  const [campus, setCampus] = useState("cs1");
  const fetchSnapshot = useCallback(async (signal) => {
    const campusCode = campus.toUpperCase();
    const [occupancy, rooms] = await Promise.all([
      getCurrentOccupancy({ signal, campus: campusCode }),
      getCampusRooms(campusCode, { signal }),
    ]);
    return { occupancy, rooms };
  }, [campus, refreshKey]);
  const {
    data: snapshot,
    isLoading,
    isRefreshing,
    error,
  } = useOccupancyPolling(fetchSnapshot);
  const occupancy = snapshot?.occupancy ?? null;
  const rooms = snapshot?.rooms ?? [];

  const updatedAt = formatUpdatedAt(occupancy?.updatedAt);
  const connectionStatus = getOccupancyConnectionStatus({
    error,
    isLoading,
    occupancy,
  });
  const location = occupancy?.location || "Thư viện UTH";
  const campusLabel = CAMPUS_LABELS[campus];
  const capacity = campus === "cs3" ? 120 : 222;
  const presentCount = Number.isInteger(occupancy?.count) && occupancy.count >= 0
    ? occupancy.count
    : null;
  const availableCount = presentCount === null
    ? null
    : Math.max(0, capacity - presentCount);
  const densityPercent = presentCount === null
    ? null
    : Math.round((presentCount / capacity) * 100);
  const campusMetrics = campus === "cs3"
    ? {
        present: presentCount === null ? "—" : String(presentCount),
        available: availableCount === null ? "—" : String(availableCount),
        capacity: String(capacity),
        density: densityPercent === null ? "—" : `${densityPercent}%`,
      }
    : {
        present: presentCount === null ? "—" : String(presentCount),
        available: availableCount === null ? "—" : String(availableCount),
        capacity: String(capacity),
        density: densityPercent === null ? "—" : `${densityPercent}%`,
      };
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
          <button type="button" className="portal-button">
            <Icon>open_in_new</Icon>
            <span>Cổng Portal UTH</span>
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
              <span className="avatar-fallback">N</span>
            </span>
            <span className="profile-copy">
              <strong>Nguyễn Văn An</strong>
              <small>MSSV: 2151050</small>
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
            label={campus === "cs3" ? "Đang có mặt tại CS3" : "Sức chứa"}
            value={campus === "cs3" ? campusMetrics.present : campusMetrics.capacity}
            unit={campus === "cs3" ? "sinh viên" : "chỗ"}
            icon="chair_alt"
            variant="primary"
            note={campus === "cs3"
              ? "Thống kê số hiện có"
              : "B301A Lầu 1, Lầu 2 & Chuyên đề"}
          />
          <MetricCard
            label={campus === "cs3" ? "Chỗ còn trống" : "Đang có mặt"}
            value={campus === "cs3" ? campusMetrics.available : campusMetrics.present}
            unit={campus === "cs3" ? "chỗ sẵn sàng" : "người"}
            icon="group"
            variant="secondary"
            note={dataSourceNote}
          />
          <MetricCard
            label={campus === "cs3" ? "Sức chứa tối đa (Tòa K)" : "Còn trống"}
            value={campus === "cs3" ? campusMetrics.capacity : campusMetrics.available}
            unit={campus === "cs3" ? "tổng chỗ ngồi (Tầng 1)" : "chỗ trống"}
            icon="event_seat"
            variant="green"
            note={campus === "cs3" ? "Tòa K - Tầng 1" : "Sẵn sàng đón tiếp"}
          />
          <MetricCard
            label="Mật độ trung bình"
            value={campusMetrics.density}
            unit=""
            icon="speed"
            variant="primary"
          >
            <div className="metric-progress">
              <span />
            </div>
          </MetricCard>
        </section>

        {presentCount !== null && presentCount > capacity && (
          <div className="alert alert--warning" role="alert">
            <Icon>warning</Icon>
            <div className="alert-content">
              <strong>⚠ Vượt sức chứa</strong>
              <span>Thư viện hiện đang vượt quá sức chứa ({presentCount}/{capacity} người, {densityPercent}%). Vui lòng kiểm soát lưu lượng vào.</span>
            </div>
          </div>
        )}

        <div className="content-grid">
          <section className="panel areas-panel">
            <div className="section-heading">
              <div>
                <Icon>analytics</Icon>
                <h2>Tình trạng mật độ — {campusLabel}</h2>
              </div>
            </div>
            <div className="area-list">
              {isLoading ? (
                <p className="data-unavailable">Đang tải dữ liệu...</p>
              ) : !occupancy ? (
                <p className="data-unavailable">Chưa có dữ liệu occupancy.</p>
              ) : (
                <div className="occupancy-summary">
                  <div className="occupancy-stat">
                    <strong>Số người hiện tại:</strong>
                    <span className="occupancy-value">{occupancy.count ?? "—"} người</span>
                  </div>
                  <div className="occupancy-stat">
                    <strong>Sức chứa:</strong>
                    <span className="occupancy-value">{capacity} chỗ</span>
                  </div>
                  <div className="occupancy-stat">
                    <strong>Mật độ:</strong>
                    <span className={`occupancy-value ${densityPercent >= 100 ? "critical" : densityPercent >= 80 ? "high" : "normal"}`}>
                      {densityPercent ?? "—"}%
                    </span>
                  </div>
                  {presentCount !== null && presentCount > capacity && (
                    <div className="occupancy-warning">
                      🔴 Vượt sức chứa ({presentCount}/{capacity})
                    </div>
                  )}
                </div>
              )}
            </div>
            {error && (
              <StaleWarning status="disconnected" lastUpdatedAt={occupancy?.updatedAt} />
            )}
            {!error && rooms.every((room) => room.is_stale) && rooms.length > 0 && (
              <StaleWarning status="stale" lastUpdatedAt={occupancy?.updatedAt} />
            )}
            {!error && !isLoading && rooms.every((room) => room.count === null) && rooms.length > 0 && (
              <StaleWarning status="insufficient" lastUpdatedAt={occupancy?.updatedAt} />
            )}
            {campus === "cs3" && (
              <div className="cs3-note" role="note">
                <Icon>info</Icon>
                <span>Không gian mở dành riêng cho sinh viên Cơ sở 3. Không gian thoáng, gồm khu tự học và đọc tài liệu.</span>
              </div>
            )}
            {!isLoading && !error && (
              <p className="panel-footnote">
                Chưa có dữ liệu phân khu từ Backend API. Số người hiện tại là
                tổng các phòng đang hoạt động, chưa lọc theo cơ sở.
              </p>
            )}
          </section>

          <aside className="right-column">
            {campus !== "cs3" && (
              <section className="panel booking-panel">
              <div className="section-heading compact">
                <div>
                  <Icon>event_available</Icon>
                  <h2>Lịch đặt phòng sắp tới</h2>
                </div>
                <span className="small-badge">Đã xác nhận</span>
              </div>
              <div className="booking-detail">
                <strong>Phòng Chuyên Đề 1 · CS1</strong>
                <span><Icon>schedule</Icon> Hôm nay 14:00 - 16:00 (còn 2 giờ)</span>
              </div>
              <div className="booking-qr">
                <span className="qr-mini"><Icon>qr_code_2</Icon></span>
                <div>
                  <strong>Quét mã trước 14:15</strong>
                  <small>Tự hủy nếu quá hạn 15 phút</small>
                </div>
              </div>
              <button type="button" className="qr-button">
                <Icon>qr_code_scanner</Icon>
                Xem mã QR Check-in
              </button>
              </section>
            )}

            <section className="panel notice-panel">
              <div className="section-heading compact">
                <div>
                  <Icon>campaign</Icon>
                  <h2>{campus === "cs3" ? "Thông báo Thư viện CS3 (Tòa K)" : "Thông báo thư viện"}</h2>
                </div>
              </div>
              {campus === "cs3" ? (
                <>
                  <div className="notice-item notice-info">
                    <strong>Khung giờ phục vụ Tòa K - Tầng 1</strong>
                    <span>Thứ 2 - Thứ 7: 07:30 - 21:00. Chủ nhật mở cửa theo lịch thi tập trung.</span>
                  </div>
                  <div className="notice-item notice-warning">
                    <strong>Quy định giữ chỗ tại chỗ</strong>
                    <span>Vui lòng đặt và di chuyển đến khu vực phòng học theo quy tắc.</span>
                  </div>
                  <div className="notice-item notice-info">
                    <strong>Văn hóa giữ chỗ</strong>
                    <span>Vui lòng không để lại đồ để giữ chỗ. Check-in bằng mã QR khi đến khu tự học.</span>
                  </div>
                </>
              ) : (
                <>
                  <div className="notice-item notice-info">
                    <strong>Giờ hạn mở cửa mùa thi 07:00 - 22:30</strong>
                    <span>Áp dụng cả 2 cơ sở từ Thứ Hai đến Thứ Bảy.</span>
                  </div>
                  <div className="notice-item notice-warning">
                    <strong>Quy định tự động hủy đặt phòng</strong>
                    <span>Phòng hủy tự động nếu chưa check-in sau 15 phút.</span>
                  </div>
                </>
              )}
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
