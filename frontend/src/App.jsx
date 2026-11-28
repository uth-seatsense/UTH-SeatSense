import {
  NavLink,
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";
import LoginPage from "./pages/LoginPage.tsx";
import RoomDetailPage from "./pages/RoomDetailPage.tsx";
import MyBookingsPage from "./pages/MyBookingsPage.jsx";
import ProfilePage from "./pages/ProfilePage.jsx";
import CheckinPage from "./pages/CheckinPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import BookingPage from "./pages/BookingPage.tsx";
import HealthPage from "./pages/HealthPage.jsx";
import { AuthProvider, useAuth } from "./auth/AuthContext.jsx";
import ProtectedRoute from "./components/ProtectedRoute.tsx";
import { useState } from "react";

const navigation = [
  ["/dashboard", "Tổng quan"],
  ["/booking", "Đặt phòng"],
  ["/my-bookings", "Lịch đặt của tôi"],
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
  const hasSidebar = path === "/" || path === "/dashboard" || path === "/booking";

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
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/rooms" element={<Navigate to="/booking" replace />} />
        <Route
          path="/rooms/:roomId"
          element={
            <ProtectedRoute>
              <RoomDetailPage />
            </ProtectedRoute>
          }
        />
        <Route path="/reservation" element={<Navigate to="/booking" replace />} />
        <Route
          path="/my-bookings"
          element={
            <ProtectedRoute>
              <MyBookingsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/checkin"
          element={
            <ProtectedRoute>
              <CheckinPage />
            </ProtectedRoute>
          }
        />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/booking" element={<BookingPage />} />
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

