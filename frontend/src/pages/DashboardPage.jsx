import { useEffect, useRef, useState } from "react";
import { getCurrentOccupancy } from "../services/api.js";

const REFRESH_INTERVAL = 30_000;

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
          <a className="side-link" href="#rooms">
            <Icon>meeting_room</Icon>
            Đặt phòng học
          </a>
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
          <strong>{isLoading ? "Đang tải" : "Chưa có dữ liệu"}</strong>
          <span>—</span>
        </div>
        <div className="area-track" aria-hidden="true">
          <span />
        </div>
      </div>
      <span className="area-status">
        {isLoading ? "Đang tải" : "Chờ cập nhật"}
      </span>
    </article>
  );
}

export default function DashboardPage() {
  const [occupancy, setOccupancy] = useState(null);
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
        const result = await getCurrentOccupancy({
          signal: controller.signal,
        });
        if (active) {
          setOccupancy(result);
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
  const statusText = error
    ? "Lỗi kết nối"
    : isLoading
      ? "Đang tải dữ liệu"
      : "Cập nhật trực tiếp";
  const statusClass = error ? "error" : isLoading ? "loading" : "";
  const displayCount = occupancy
    ? new Intl.NumberFormat("vi-VN").format(occupancy.count)
    : "—";
  const countValue = displayCount;
  const location = occupancy?.location || "Thư viện UTH";
  const campusLabel =
    campus === "cs1" ? "Cơ sở 1 (Võ Oanh - B.301A)" : "Cơ sở 3 (Tòa K - Lầu 1)";

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
            <span className={`connection-pill ${statusClass}`} role="status">
              <span className="status-dot" />
              {updatedAt ? `Cập nhật: ${updatedAt}` : statusText}
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
              Cơ sở 1 (Võ Oanh - B.301A)
            </button>
            <button
              type="button"
              className={campus === "cs3" ? "selected" : ""}
              aria-pressed={campus === "cs3"}
              onClick={() => setCampus("cs3")}
            >
              <Icon>location_city</Icon>
              Cơ sở 3 (Tòa K - Lầu 2)
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
            value="—"
            unit="chỗ"
            icon="chair_alt"
            variant="primary"
            note="Chưa có dữ liệu sức chứa"
          />
          <MetricCard
            label="Đang có mặt"
            value={countValue}
            unit="người"
            icon="group"
            variant="secondary"
            note={isRefreshing ? "Đang làm mới dữ liệu" : "Dữ liệu từ Backend API"}
          />
          <MetricCard
            label="Còn trống"
            value="—"
            unit="chỗ trống"
            icon="event_seat"
            variant="green"
            note="Chưa có dữ liệu sức chứa"
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
              {areas.map((area) => (
                <AreaRow key={area.name} area={area} isLoading={isLoading} />
              ))}
            </div>
            {!isLoading && !error && (
              <p className="panel-footnote">
                Chưa có dữ liệu phân khu từ Backend API. Số người hiện tại là
                tổng các phòng đang hoạt động, chưa lọc theo cơ sở.
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
