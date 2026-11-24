import {
  NavLink,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";
import HomePage from "./pages/HomePage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import RoomsPage from "./pages/RoomsPage.jsx";
import RoomDetailPage from "./pages/RoomDetailPage.tsx";
import ReservationPage from "./pages/ReservationPage.jsx";
import MyBookingsPage from "./pages/MyBookingsPage.jsx";
import CheckinPage from "./pages/CheckinPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import HealthPage from "./pages/HealthPage.jsx";
import { AuthProvider, useAuth } from "./auth/AuthContext.jsx";
import RequireAuth from "./auth/RequireAuth.jsx";
import { useState } from "react";

const navigation = [
  ["/", "Trang chủ"],
  ["/rooms", "Danh sách phòng"],
  ["/reservation", "Đặt phòng"],
  ["/my-bookings", "Lịch đặt của tôi"],
  ["/checkin", "Xác nhận có mặt"],
  ["/dashboard", "Tổng quan"],
];

export default function App() {
  return (
    <AuthProvider>
      <Application />
    </AuthProvider>
  );
}

function Application() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { user, signOut } = useAuth();
  const [navigationError, setNavigationError] = useState("");
  const path = pathname.replace(/\/+$/, "") || "/";
  const hasSidebar = path === "/" || path === "/dashboard";

  return (
    <>
      {!hasSidebar && (
        <nav
          aria-label="Điều hướng chính"
          className="app-navigation"
        >
          <div className="app-navigation-links">
            {navigation.map(([to, label]) => (
              <NavLink key={to} to={to} end>
                {label}
              </NavLink>
            ))}
          </div>
          {user ? (
            <div className="app-navigation-account">
              <span>{user.display_name || user.email}</span>
              <button
                className="button button--quiet"
                onClick={async () => {
                  setNavigationError("");
                  try {
                    await signOut();
                    navigate("/login", { replace: true });
                  } catch (error) {
                    setNavigationError(error.message);
                  }
                }}
                type="button"
              >
                Đăng xuất
              </button>
            </div>
          ) : (
            <NavLink className="app-navigation-login" to="/login" end>
              Đăng nhập
            </NavLink>
          )}
        </nav>
      )}
      {navigationError && (
        <p
          className="feedback feedback--error navigation-feedback"
          role="alert"
        >
          Đã đăng xuất khỏi thiết bị nhưng máy chủ chưa xác nhận:{" "}
          {navigationError}
        </p>
      )}
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/rooms"
          element={
            <RequireAuth>
              <RoomsPage />
            </RequireAuth>
          }
        />
        <Route
          path="/rooms/:roomId"
          element={
            <RequireAuth>
              <RoomDetailPage />
            </RequireAuth>
          }
        />
        <Route
          path="/reservation"
          element={
            <RequireAuth>
              <ReservationPage />
            </RequireAuth>
          }
        />
        <Route
          path="/my-bookings"
          element={
            <RequireAuth>
              <MyBookingsPage />
            </RequireAuth>
          }
        />
        <Route
          path="/checkin"
          element={
            <RequireAuth>
              <CheckinPage />
            </RequireAuth>
          }
        />
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
