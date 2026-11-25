import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getCurrentUser } from "../services/api.js";

const ROLE_LABELS = {
  student: "Sinh viên",
  librarian: "Thủ thư",
  admin: "Quản trị viên",
};

export default function ProfilePage() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    async function loadProfile() {
      setLoading(true);
      setError("");
      try {
        const profile = await getCurrentUser({ signal: controller.signal });
        if (active) setUser(profile);
      } catch (loadError) {
        if (active && loadError.name !== "AbortError") {
          setError(loadError.message);
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    loadProfile();
    return () => {
      active = false;
      controller.abort();
    };
  }, []);

  return (
    <main className="feature-page">
      <header className="feature-heading">
        <p className="eyebrow">Tài khoản của bạn</p>
        <h1>Hồ sơ sinh viên</h1>
        <p>Thông tin tài khoản và quyền truy cập của bạn.</p>
      </header>

      {loading && (
        <p className="loading-message" aria-live="polite">
          Đang tải thông tin...
        </p>
      )}

      {error && (
        <div className="feedback feedback--error" role="alert">
          Không thể tải thông tin: {error}
        </div>
      )}

      {!loading && !error && user && (
        <div className="profile-container">
          <section className="feature-panel">
            <h2>Thông tin cá nhân</h2>

            <div className="profile-field">
              <label className="profile-field__label">Họ và tên</label>
              <p className="profile-field__value">{user.display_name}</p>
            </div>

            <div className="profile-field">
              <label className="profile-field__label">Email</label>
              <p className="profile-field__value">{user.email}</p>
            </div>

            <div className="profile-field">
              <label className="profile-field__label">Vai trò</label>
              <p className="profile-field__value">
                {ROLE_LABELS[user.role] || user.role}
              </p>
            </div>

            <div className="profile-field">
              <label className="profile-field__label">Mã người dùng</label>
              <p className="profile-field__value">#{user.id}</p>
            </div>
          </section>

          <section className="feature-panel">
            <h2>Hoạt động</h2>
            <div className="profile-actions">
              <Link className="button button--primary" to="/my-bookings">
                Xem lịch đặt của tôi
              </Link>
              <Link className="button button--secondary" to="/reservation">
                Đặt phòng mới
              </Link>
            </div>
          </section>
        </div>
      )}
    </main>
  );
}
