import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext.jsx";
import { requestLoginOtp } from "../services/api.js";

export default function LoginPage() {
  const { user, login } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [otpRequested, setOtpRequested] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(location.state?.authError ?? "");
  const [notice, setNotice] = useState("");

  if (user) return <Navigate to="/rooms" replace />;

  async function sendOtp(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await requestLoginOtp(email.trim());
      setOtpRequested(true);
      setNotice("Nếu email được phép, mã xác minh sẽ được gửi đến hộp thư.");
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  }

  async function verifyOtp(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(email.trim(), otp);
      const destination = location.state?.from?.pathname ?? "/rooms";
      navigate(destination, { replace: true });
    } catch (loginError) {
      setError(loginError.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="feature-page feature-page--narrow">
      <header className="feature-heading">
        <p className="eyebrow">UTH SeatSense</p>
        <h1>Đăng nhập bằng email</h1>
        <p>
          Nhận mã OTP qua email được nhà trường cho phép để dùng các chức năng
          đặt phòng.
        </p>
      </header>

      <form
        className="feature-panel feature-form"
        onSubmit={otpRequested ? verifyOtp : sendOtp}
      >
        <label className="form-field">
          <span>Email</span>
          <input
            autoComplete="email"
            disabled={busy || otpRequested}
            onChange={(event) => setEmail(event.target.value)}
            required
            type="email"
            value={email}
          />
        </label>

        {otpRequested && (
          <label className="form-field">
            <span>Mã OTP 6 chữ số</span>
            <input
              autoComplete="one-time-code"
              inputMode="numeric"
              maxLength={6}
              onChange={(event) =>
                setOtp(event.target.value.replace(/\D/g, "").slice(0, 6))
              }
              pattern="[0-9]{6}"
              required
              value={otp}
            />
          </label>
        )}

        {error && (
          <p className="feedback feedback--error" role="alert">
            {error}
          </p>
        )}
        {notice && (
          <p className="feedback feedback--success" role="status">
            {notice}
          </p>
        )}

        <button
          className="button button--primary"
          disabled={busy}
          type="submit"
        >
          {busy
            ? "Đang xử lý..."
            : otpRequested
              ? "Xác minh và đăng nhập"
              : "Gửi mã OTP"}
        </button>
        {otpRequested && (
          <button
            className="button button--quiet"
            disabled={busy}
            onClick={() => {
              setOtpRequested(false);
              setOtp("");
              setNotice("");
            }}
            type="button"
          >
            Đổi email
          </button>
        )}
        <Link className="text-link" to="/">
          Về trang tổng quan
        </Link>
      </form>
    </main>
  );
}
