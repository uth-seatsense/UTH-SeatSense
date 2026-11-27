import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getCurrentOccupancy, getRoomOccupancyStatus, isMockEnabled } from "../services/api.js";
import { useAuth } from "../auth/AuthContext.jsx";

const REFRESH_INTERVAL = 30_000;
const CAMPUSES = {
  cs1: { api: "CS1", label: "Cơ sở 1 (Võ Oanh - B.301A)", short: "Cơ sở 1 (Võ Oanh)" },
  cs3: { api: "CS3", label: "Cơ sở 3 (Tòa K - Lầu 1)", short: "Cơ sở 3 (Tòa K)" },
};
const DEMO_ROOMS = {
  cs1: [
    { room_id: "demo-cs1-1", room_code: "B301A-L1", room_name: "B301A - Lầu 1", capacity: 120, current_count: 48, description: "Bàn rộng cắm sạc điện thoại & laptop", category: "Tự học & Máy tính" },
    { room_id: "demo-cs1-2", room_code: "B301A-L2", room_name: "B301A - Lầu 2", capacity: 80, current_count: 26, description: "Không gian nghiên cứu tài liệu", category: "Đọc sách yên tĩnh" },
    { room_id: "demo-cs1-3", room_code: "PCD1", room_name: "Phòng Chuyên Đề 1", capacity: 12, current_count: 6, description: "Trang bị SmartTV & Bảng viết kính", category: "Học nhóm 10-12 bạn" },
    { room_id: "demo-cs1-4", room_code: "PCD2", room_name: "Phòng Chuyên Đề 2", capacity: 10, current_count: 0, description: "Trang bị màn chiếu tương tác & Wifi tốc độ cao", category: "Học nhóm 8-10 bạn" },
  ],
  cs3: [
    { room_id: "demo-cs3-1", room_code: "CS3-TK1", room_name: "Toàn sàn tự học mở Tầng 1 (Tòa K)", capacity: 120, current_count: 48, description: "Không gian chung, không áp dụng đặt phòng trước", category: "Tự học & Đọc sách" },
  ],
};
const NOTICES = [
  { title: "Khung giờ phục vụ", body: "Thứ Hai - Thứ Bảy: 07:30 - 21:00. Chủ nhật mở cửa theo lịch thi.", tone: "info" },
  { title: "Quy định check-in", body: "Quét mã QR trong vòng 15 phút từ giờ bắt đầu để giữ lượt đặt.", tone: "warning" },
  { title: "Giữ gìn không gian chung", body: "Vui lòng giữ yên tĩnh tại khu vực tự học và trả lại chỗ ngồi gọn gàng.", tone: "success" },
];

function Icon({ children, className = "" }) {
  return <span className={`material-symbols-outlined ${className}`} aria-hidden="true">{children}</span>;
}
function formatTime(value) {
  if (!value) return "Chưa có dữ liệu";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  const olderThanDay = Date.now() - date.getTime() > 86_400_000;
  const options = olderThanDay
    ? { dateStyle: "short", timeStyle: "short" }
    : { hour: "2-digit", minute: "2-digit", second: "2-digit" };
  return new Intl.DateTimeFormat("vi-VN", options).format(date);
}
function Metric({ label, value, unit, icon, tone, note, progress }) {
  return <section className="dash-metric"><div className="dash-metric-head"><span>{label}</span><Icon className={tone}>{icon}</Icon></div><div className={`dash-metric-value ${tone}`}>{value}<small>{unit}</small></div>{progress != null ? <><span className="dash-density-pill">{progress < 50 ? "Thoáng đãng" : progress < 80 ? "Vừa phải" : "Đông"}</span><div className="dash-progress"><i style={{ width: `${Math.min(progress, 100)}%` }} /></div></> : <p>{note}</p>}</section>;
}
function RoomRow({ room, onSelect }) {
  const count = Number.isInteger(room.current_count) ? room.current_count : null;
  const capacity = Number.isInteger(room.capacity) ? room.capacity : null;
  const percent = count != null && capacity ? Math.round(count / capacity * 100) : null;
  const available = room.available_seats ?? (count != null && capacity ? Math.max(capacity - count, 0) : null);
  const status = percent == null ? "Chưa có dữ liệu" : percent >= 70 ? "Đang dùng" : percent >= 40 ? "Thoáng" : "Rất thoáng";
  return <article className="dash-room-row"><button className="dash-room-name" type="button" onClick={() => onSelect(room)}><strong>{room.room_name}</strong><span>{room.category ?? room.room_code}</span><small>Sức chứa {capacity ?? "—"} chỗ • {room.description ?? room.room_code}</small></button><div className="dash-room-count"><strong>{count ?? "—"} / {capacity ?? "—"}</strong><span>{percent == null ? "—" : `${percent}%`}</span><div className="dash-progress"><i style={{ width: `${percent ?? 0}%` }} /></div></div><span className={`dash-room-status ${percent == null ? "unknown" : percent >= 70 ? "busy" : "free"}`}>{status}</span></article>;
}

export default function DashboardPage() {
  const { user, signOut } = useAuth();
  const [campus, setCampus] = useState("cs1");
  const [occupancy, setOccupancy] = useState(null);
  const [roomStatus, setRoomStatus] = useState(null);
  const [error, setError] = useState("");
  const [detailError, setDetailError] = useState("");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [search, setSearch] = useState("");
  const [noticesOpen, setNoticesOpen] = useState(false);
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [profileError, setProfileError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    let timeout;
    const load = async () => {
      setLoading((current) => occupancy ? current : true);
      setRefreshing(Boolean(occupancy));
      setError("");
      try {
        const [summaryResult, detailResult] = await Promise.allSettled([
          getCurrentOccupancy({ signal: controller.signal, campus: CAMPUSES[campus].api }),
          getRoomOccupancyStatus({ signal: controller.signal, campus: CAMPUSES[campus].api }),
        ]);
        if (!active) return;
        if (summaryResult.status === "fulfilled") {
          setOccupancy(summaryResult.value);
          setError("");
        } else {
          setError(summaryResult.reason?.message || "Không thể tải số người hiện tại.");
        }
        if (detailResult.status === "fulfilled") {
          setRoomStatus(detailResult.value);
          setDetailError("");
        } else {
          setRoomStatus(null);
          setDetailError(detailResult.reason?.message || "Không thể tải chi tiết sức chứa phòng.");
        }      } finally {
        if (active) {
          setLoading(false);
          setRefreshing(false);
          timeout = window.setTimeout(load, REFRESH_INTERVAL);
        }
      }
    };
    load();
    return () => { active = false; controller.abort(); window.clearTimeout(timeout); };
  }, [campus, refreshKey]);

  const usingDemo = isMockEnabled() && !roomStatus?.rooms?.length;
  const rooms = roomStatus?.rooms?.length ? roomStatus.rooms : usingDemo ? DEMO_ROOMS[campus] : [];
  const visibleRooms = useMemo(() => rooms.filter((room) => `${room.room_name} ${room.room_code} ${room.category ?? ""} ${room.description ?? ""}`.toLocaleLowerCase("vi").includes(search.trim().toLocaleLowerCase("vi"))), [rooms, search]);
  const capacity = rooms.reduce((sum, room) => sum + (room.capacity ?? 0), 0);
  const present = usingDemo ? rooms.reduce((sum, room) => sum + (room.current_count ?? 0), 0) : occupancy?.count ?? rooms.reduce((sum, room) => sum + (room.current_count ?? 0), 0);
  const available = rooms.reduce((sum, room) => sum + (room.available_seats ?? Math.max((room.capacity ?? 0) - (room.current_count ?? 0), 0)), 0);
  const density = capacity ? Math.round((present ?? 0) / capacity * 100) : null;
  const updatedAt = occupancy?.updatedAt ?? roomStatus?.updated_at ?? roomStatus?.last_updated;
  const cameraDisconnected = occupancy?.dataStatus === "disconnected";
  const connectionTone = error || cameraDisconnected ? "error" : loading ? "loading" : "";
  const connectionText = error ? "Không thể tải số người hiện tại" : loading ? "Đang cập nhật..." : cameraDisconnected ? `Camera mất kết nối · số cuối cùng ghi nhận ${formatTime(updatedAt)}` : occupancy?.dataStatus === "stale" ? `Dữ liệu đã cũ · cập nhật ${formatTime(updatedAt)}` : `Cập nhật: ${formatTime(updatedAt)}${refreshing ? " (đang làm mới)" : ""}`;
  const displayName = user?.display_name || user?.email?.split("@")[0] || "Sinh viên UTH";
  const studentId = user?.email?.split("@")[0] || "Đăng nhập để đồng bộ";

  return <div className="dashboard-v2">
    <aside className="dash-sidebar"><div><Link to="/dashboard" className="dash-brand"><span><Icon>school</Icon></span><div><strong>UTH-SeatSense</strong><small>Đại học Giao thông Vận tải</small></div></Link><nav className="dash-nav" aria-label="Điều hướng"><Link className="current" to="/dashboard"><Icon>dashboard</Icon>Tổng quan</Link><Link to="/booking"><Icon>meeting_room</Icon>Đặt phòng học</Link><Link to="/my-bookings"><Icon>history</Icon>Lịch đặt</Link></nav></div><div className="dash-nav dash-nav-bottom"><a href="#notices"><Icon>help</Icon>Hỗ trợ &amp; Hướng dẫn</a><button type="button" onClick={() => setNoticesOpen((open) => !open)}><Icon>settings</Icon>Cài đặt hệ thống</button></div></aside>
    <div className="dash-workspace"><header className="dash-topbar"><label className="dash-search"><Icon>search</Icon><input value={search} onChange={(event) => setSearch(event.target.value)} type="search" placeholder="Tìm tầng, phòng, bàn học hoặc vị trí..." aria-label="Tìm khu vực" /></label><button type="button" className="dash-top-button" onClick={() => document.getElementById("dash-areas")?.scrollIntoView({ behavior: "smooth" })}><Icon>map</Icon>Sơ đồ trường</button><a className="dash-top-button portal" href="https://portal.ut.edu.vn" target="_blank" rel="noreferrer"><Icon>open_in_new</Icon>Cổng Portal UTH</a><div className="dash-top-spacer" /><button type="button" className={`dash-notice-button ${noticesOpen ? "active" : ""}`} aria-label="Thông báo thư viện" aria-expanded={noticesOpen} onClick={() => setNoticesOpen((open) => !open)}><Icon>notifications</Icon><i /></button><span className="dash-divider" />{user ? <div className="dash-profile"><span className="dash-avatar">{displayName.slice(0, 1).toLocaleUpperCase("vi")}</span><span><strong>{displayName}</strong><small>MSSV: {studentId}</small></span><button type="button" onClick={async () => { setProfileError(""); try { await signOut(); } catch (signOutError) { setProfileError(signOutError.message); } }}>Đăng xuất</button></div> : <Link className="dash-profile dash-profile-login" to="/login" state={{ from: { pathname: "/dashboard" } }}><span className="dash-avatar"><Icon>person</Icon></span><span><strong>Đăng nhập</strong><small>Để đồng bộ tài khoản</small></span></Link>}</header>
    {noticesOpen && <section className="dash-notice-popover" role="dialog" aria-label="Thông báo thư viện"><header><strong>Thông báo mới nhất</strong><button type="button" onClick={() => setNoticesOpen(false)} aria-label="Đóng thông báo">×</button></header>{NOTICES.map((notice) => <article className={`dash-notice ${notice.tone}`} key={notice.title}><strong>{notice.title}</strong><p>{notice.body}</p></article>)}</section>}
    <main className="dash-main"><div className="dash-heading"><div className="dash-heading-main"><h1>Tổng quan Thư viện UTH</h1><span className={`dash-update ${connectionTone}`} role="status"><i />{connectionText}</span><button className="dash-refresh" type="button" aria-label="Làm mới dữ liệu" onClick={() => setRefreshKey((value) => value + 1)}><Icon>refresh</Icon></button></div><div className="dash-campus-switch" role="group" aria-label="Chọn cơ sở">{Object.entries(CAMPUSES).map(([id, item]) => <button type="button" key={id} className={campus === id ? "selected" : ""} aria-pressed={campus === id} onClick={() => { setCampus(id); setSelectedRoom(null); }}><Icon>domain</Icon>{item.label}</button>)}</div></div>
      {error && <div className="dash-alert" role="alert"><Icon>error</Icon><span>{error}</span><button type="button" onClick={() => setRefreshKey((value) => value + 1)}>Thử lại</button></div>}{detailError && !error && <div className="dash-alert dash-warning" role="status"><Icon>info</Icon><span>{detailError} {"S\u1ed1 ng\u01b0\u1eddi t\u1ed5ng t\u1eeb API v\u1eabn hi\u1ec3n th\u1ecb ri\u00eang."}</span></div>}{profileError && <div className="dash-alert" role="alert">{profileError}</div>}
      <section className="dash-metrics" aria-label="Thống kê thư viện"><Metric label="Sức chứa" value={capacity ? capacity.toLocaleString("vi-VN") : "—"} unit="chỗ" icon="chair_alt" tone="navy" note={campus === "cs1" ? "B301A Lầu 1, Lầu 2 & Chuyên đề" : "Không gian tự học Tòa K"} /><Metric label="Đang có mặt" value={present == null ? "—" : present.toLocaleString("vi-VN")} unit="sinh viên" icon="groups" tone="blue" note={usingDemo ? "AI đếm trực tiếp • dữ liệu mẫu" : cameraDisconnected ? "Camera ngắt kết nối • số cuối cùng từ API" : occupancy?.dataStatus === "stale" ? "Dữ liệu API đã cũ" : "Dữ liệu API cập nhật mỗi 30 giây"} /><Metric label="Còn trống" value={capacity ? available.toLocaleString("vi-VN") : "—"} unit="chỗ trống" icon="event_seat" tone="green" note="Sẵn sàng đón tiếp" /><Metric label="Mật độ trung bình" value={density == null ? "—" : `${density}%`} unit="" icon="speed" tone="navy" progress={density} /></section>
      <div className="dash-content-grid"><section id="dash-areas" className="dash-panel dash-areas-panel"><header className="dash-panel-heading"><div><Icon>analytics</Icon><h2>Mật độ các khu vực — {CAMPUSES[campus].short}</h2></div><span>{rooms.length} khu vực</span></header><p className="dash-panel-intro">Theo dõi tình trạng chỗ ngồi được cập nhật tự động. Chọn một khu vực để xem danh sách phòng phù hợp.</p><div className="dash-room-list">{visibleRooms.map((room) => <RoomRow key={room.room_id ?? room.room_code} room={room} onSelect={setSelectedRoom} />)}{!visibleRooms.length && <p className="dash-no-results">{rooms.length ? "Không tìm thấy khu vực phù hợp." : loading ? "Đang tải dữ liệu khu vực..." : "Chưa có dữ liệu khu vực."}</p>}</div>{selectedRoom && <div className="dash-selected-room"><Icon>info</Icon><span><strong>{selectedRoom.room_name}</strong> · {selectedRoom.description ?? selectedRoom.room_code}</span><button type="button" onClick={() => setSelectedRoom(null)} aria-label="Đóng chi tiết">×</button></div>}<div className="dash-compare"><Icon>compare_arrows</Icon><div><strong>Đối chiếu nhanh với {campus === "cs1" ? CAMPUSES.cs3.short : CAMPUSES.cs1.short}</strong><p>Dữ liệu chỗ ngồi và mức sử dụng theo từng cơ sở.</p></div><button type="button" onClick={() => setCampus(campus === "cs1" ? "cs3" : "cs1")}>Xem cơ sở kia <Icon>arrow_forward</Icon></button></div></section>
      <aside className="dash-right-column"><section className="dash-panel dash-upcoming"><header className="dash-panel-heading"><div><Icon>event_available</Icon><h2>Lịch đặt phòng sắp tới</h2></div><span className="dash-confirmed">{user ? "Tài khoản đã kết nối" : "Cần đăng nhập"}</span></header>{user ? <div className="dash-booking-empty"><Icon>event_busy</Icon><strong>Chưa có lượt đặt sắp tới</strong><p>Chọn phòng và khung giờ phù hợp để tạo lượt đặt mới.</p><Link to="/booking" className="dash-primary-link">Đặt phòng học</Link></div> : <div className="dash-booking-empty"><Icon>account_circle</Icon><strong>Đăng nhập để xem lịch đặt</strong><p>Lịch đặt và mã check-in sẽ hiển thị tại đây.</p><Link to="/login" state={{ from: { pathname: "/dashboard" } }} className="dash-primary-link">Đăng nhập bằng OTP</Link></div>}<Link to="/my-bookings" className="dash-secondary-link">Mở lịch đặt của tôi <Icon>arrow_forward</Icon></Link></section>
      <section id="notices" className="dash-panel dash-notices"><header className="dash-panel-heading"><div><Icon>campaign</Icon><h2>Thông báo thư viện</h2></div><span>Hôm nay</span></header>{NOTICES.map((notice) => <article className={`dash-notice ${notice.tone}`} key={notice.title}><strong>{notice.title}</strong><p>{notice.body}</p></article>)}</section></aside></div>
      <footer className="dash-footer">UTH-SeatSense · {occupancy?.location || "Thư viện UTH"} · {isMockEnabled() ? "Dữ liệu minh họa" : "Dữ liệu từ Backend API"}</footer>
    </main></div></div>;
}




