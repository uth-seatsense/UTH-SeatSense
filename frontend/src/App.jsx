import { NavLink, Route, Routes, useLocation } from "react-router-dom";
import HomePage from "./pages/HomePage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import RoomsPage from "./pages/RoomsPage.jsx";
import ReservationPage from "./pages/ReservationPage.jsx";
import MyBookingsPage from "./pages/MyBookingsPage.jsx";
import CheckinPage from "./pages/CheckinPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import HealthPage from "./pages/HealthPage.jsx";

const navigation = [
  ["/", "Trang chủ"],
  ["/rooms", "Danh sách phòng"],
  ["/reservation", "Đặt phòng"],
  ["/my-bookings", "Lịch đặt của tôi"],
  ["/checkin", "Xác nhận có mặt"],
  ["/dashboard", "Tổng quan"],
];

export default function App() {
  const { pathname } = useLocation();
  const path = pathname.replace(/\/+$/, "") || "/";
  const hasSidebar = path === "/" || path === "/dashboard";

  return (
    <>
      <nav
        aria-label="Điều hướng chính"
        className={`app-navigation${hasSidebar ? " app-navigation--dashboard" : ""}`}
      >
        <div className="app-navigation-links">
          {navigation.map(([to, label]) => (
            <NavLink key={to} to={to} end>
              {label}
            </NavLink>
          ))}
        </div>
        <NavLink className="app-navigation-login" to="/login" end>
          Đăng nhập
        </NavLink>
      </nav>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/rooms" element={<RoomsPage />} />
        <Route path="/reservation" element={<ReservationPage />} />
        <Route path="/my-bookings" element={<MyBookingsPage />} />
        <Route path="/checkin" element={<CheckinPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/health" element={<HealthPage />} />
        <Route
          path="*"
          element={
            <main className="skeleton-page">
              <h1>404</h1>
              <p>Không tìm thấy trang.</p>
              <NavLink to="/">Về trang chủ</NavLink>
            </main>
          }
        />
      </Routes>
    </>
  );
}
