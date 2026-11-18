import { Link, useLocation } from "react-router-dom";
import { useAuth } from "./AuthContext.jsx";

export default function RequireAuth({ children }) {
  const { user, status, authError } = useAuth();
  const location = useLocation();

  if (status === "loading") {
    return (
      <main className="feature-page" role="status">
        Đang kiểm tra phiên đăng nhập...
      </main>
    );
  }
  if (!user) {
    return (
      <main className="feature-page feature-page--narrow">
        <section className="feature-panel feature-form">
          <h1>Cần đăng nhập</h1>
          <p>Đăng nhập để xem phòng và quản lý lượt đặt của bạn.</p>
          {authError && (
            <p className="feedback feedback--error" role="alert">
              {authError}
            </p>
          )}
          <Link
            className="button button--primary"
            state={{ from: location }}
            to="/login"
          >
            Đăng nhập bằng OTP
          </Link>
        </section>
      </main>
    );
  }
  return children;
}
