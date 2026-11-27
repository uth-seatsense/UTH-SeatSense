import { useState, useEffect, useRef } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext.jsx";
import { requestLoginOtp } from "../services/api.js";

const MOCK_EMAIL_HINT = "21510509213@ut.edu.vn";

const OTP_TTL_SECONDS = 300; // 5 phút
const RESEND_COOLDOWN = 45;

function pad2(n: number) {
  return String(n).padStart(2, "0");
}

function formatCountdown(secs: number) {
  const m = Math.floor(secs / 60);
  const s = secs % 60;
  return `${pad2(m)}:${pad2(s)}`;
}

export default function LoginPage() {
  const { user, login } = useAuth() as {
    user: unknown;
    login: (email: string, otp: string) => Promise<void>;
  };
  const location = useLocation();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [step, setStep] = useState<"email" | "otp">("email");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(
    (location.state as { authError?: string })?.authError ?? ""
  );
  const [rememberDevice, setRememberDevice] = useState(false);

  /* countdown OTP validity */
  const [otpTtl, setOtpTtl] = useState(OTP_TTL_SECONDS);
  /* resend cooldown */
  const [resendCooldown, setResendCooldown] = useState(0);
  const otpTimerRef = useRef<number | null>(null);
  const resendTimerRef = useRef<number | null>(null);

  /* start / clear timers on step change */
  useEffect(() => {
    if (step === "otp") {
      setOtpTtl(OTP_TTL_SECONDS);
      setResendCooldown(RESEND_COOLDOWN);

      otpTimerRef.current = setInterval(() => {
        setOtpTtl((t) => Math.max(0, t - 1));
      }, 1000);
      resendTimerRef.current = setInterval(() => {
        setResendCooldown((c) => {
          if (c <= 1) {
            clearInterval(resendTimerRef.current!);
            return 0;
          }
          return c - 1;
        });
      }, 1000);
    }
    return () => {
      if (otpTimerRef.current) clearInterval(otpTimerRef.current);
      if (resendTimerRef.current) clearInterval(resendTimerRef.current);
    };
  }, [step]);

  if (user) return <Navigate to="/dashboard" replace />;

  /* ── Step 1: request OTP ──────────────────────────────────────────────── */
  async function handleSendOtp(event: React.FormEvent) {
    event.preventDefault();
    const normalizedEmail = email.trim().toLowerCase();
    if (!normalizedEmail.endsWith("@ut.edu.vn")) {
      setError("Vui lòng dùng email sinh viên có đuôi @ut.edu.vn.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      await requestLoginOtp(normalizedEmail);
      setEmail(normalizedEmail);
      setOtp("");
      setStep("otp");
    } catch (err: unknown) {
      setError((err as Error).message || "Không gửi được mã OTP. Hãy kiểm tra cấu hình gửi thư rồi thử lại.");
    } finally {
      setBusy(false);
    }
  }

  async function handleVerifyOtp(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      if (otpTtl <= 0) {
        throw new Error("M\u00e3 OTP \u0111\u00e3 h\u1ebft h\u1ea1n. H\u00e3y g\u1eedi l\u1ea1i m\u00e3 m\u1edbi.");
      }
      await login(email.trim(), otp);
      const destination =
        (location.state as { from?: { pathname: string } })?.from?.pathname ??
        "/dashboard";
      navigate(destination, { replace: true });
    } catch (err: unknown) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function handleResend() {
    if (resendCooldown > 0) return;
    setBusy(true);
    setError("");
    try {
      await requestLoginOtp(email.trim());
      setOtpTtl(OTP_TTL_SECONDS);
      setResendCooldown(RESEND_COOLDOWN);
      if (resendTimerRef.current) clearInterval(resendTimerRef.current);
      resendTimerRef.current = setInterval(() => {
        setResendCooldown((c) => {
          if (c <= 1) {
            if (resendTimerRef.current) clearInterval(resendTimerRef.current);
            return 0;
          }
          return c - 1;
        });
      }, 1000);
    } catch (err: unknown) {
      setError((err as Error).message || "Không gửi lại được mã OTP. Vui lòng thử lại sau.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="lp-root">
      {/* ── Header ─────────────────────────────────────────────────────── */}
      <header className="lp-header">
        <div className="lp-brand">
          <div className="lp-brand-mark">
            <span className="material-symbols-outlined">table_restaurant</span>
          </div>
          <div className="lp-brand-copy">
            <strong>UTH-SeatSense</strong>
            <small>Trường ĐH Giao thông Vận tải TP.HCM</small>
          </div>
        </div>
        <nav className="lp-header-nav" aria-label="Điều hướng phụ">
          <a href="#" className="lp-nav-link">Quy định thư viện</a>
          <a href="#" className="lp-nav-link">Hỗ trợ kỹ thuật</a>
          <a
            href="https://portal.ut.edu.vn"
            target="_blank"
            rel="noreferrer"
            className="lp-portal-btn"
          >
            Cổng thông tin ĐH GTVT
            <span className="material-symbols-outlined" style={{ fontSize: 14 }}>open_in_new</span>
          </a>
          <button className="lp-icon-btn" aria-label="Ngôn ngữ">
            <span className="material-symbols-outlined">language</span>
          </button>
          <button className="lp-icon-btn" aria-label="Trợ giúp">
            <span className="material-symbols-outlined">help_outline</span>
          </button>
        </nav>
      </header>

      {/* ── Background ─────────────────────────────────────────────────── */}
      <div className="lp-bg" aria-hidden="true" />

      {/* ── Main content ───────────────────────────────────────────────── */}
      <main className="lp-main">
        <div className="lp-card" role="region" aria-label="Đăng nhập sinh viên">
          {/* eyebrow */}
          <div className="lp-eyebrow-wrap">
            <span className="lp-eyebrow">
              <span className="material-symbols-outlined" style={{ fontSize: 13 }}>school</span>
              ĐĂNG NHẬP CỔNG SINH VIÊN
            </span>
          </div>

          <h1 className="lp-title">Đăng nhập sinh viên</h1>
          <p className="lp-subtitle">
            Xác thực mã OTP hoặc sử dụng tài khoản Cổng Đào Tạo
          </p>

          {/* ── Error alert ──────────────────────────────────────────── */}
          {error && (
            <div className="lp-alert" role="alert">
              <span className="material-symbols-outlined lp-alert-icon">error</span>
              <div className="lp-alert-body">
                <strong>Xác thực không thành công:</strong>{" "}
                {error}
              </div>
            </div>
          )}

          {/* ── Form ─────────────────────────────────────────────────── */}
          <form onSubmit={step === "email" ? handleSendOtp : handleVerifyOtp}>
            {/* Email field */}
            <div className="lp-field-group">
              <div className="lp-field-label-row">
                <label className="lp-label" htmlFor="lp-email">
                  Email trường (@ut.edu.vn) <span className="lp-required">*</span>
                </label>
                <span className="lp-hint">VD: {MOCK_EMAIL_HINT}</span>
              </div>
              <div className="lp-input-row">
                <span className="lp-input-icon material-symbols-outlined">mail</span>
                <input
                  id="lp-email"
                  className="lp-input lp-input--with-btn"
                  type="email"
                  autoComplete="email"
                  placeholder="masinhvien@ut.edu.vn"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={busy || step === "otp"}
                  required
                />
                {step === "email" ? (
                  <button
                    type="submit"
                    className="lp-send-btn"
                    disabled={busy || !email.trim()}
                  >
                    {busy ? "Đang gửi…" : "Gửi mã OTP"}
                  </button>
                ) : (
                  <button
                    type="button"
                    className="lp-change-btn"
                    onClick={() => {
                      setStep("email");
                      setOtp("");
                      setError("");
                    }}
                  >
                    Đổi email
                  </button>
                )}
              </div>
            </div>

            {/* OTP field — only shown after email submitted */}
            {step === "otp" && (
              <>
                <div className="lp-field-group lp-field-group--mt">
                  <div className="lp-field-label-row">
                    <label className="lp-label" htmlFor="lp-otp">
                      Mã xác thực OTP (6 chữ số) <span className="lp-required">*</span>
                    </label>
                    <span className="lp-otp-ttl">
                      <span
                        className="material-symbols-outlined"
                        style={{ fontSize: 13, color: otpTtl < 60 ? "#ba1a1a" : "#b76b00" }}
                      >schedule</span>
                      Mã có hiệu lực trong{" "}
                      <span style={{ color: otpTtl < 60 ? "#ba1a1a" : "#b76b00", fontWeight: 650 }}>
                        {formatCountdown(otpTtl)}
                      </span>
                    </span>
                  </div>
                  <div className="lp-input-row">
                    <span className="lp-input-icon material-symbols-outlined">pin</span>
                    <input
                      id="lp-otp"
                      className="lp-input lp-otp-input"
                      type="text"
                      inputMode="numeric"
                      autoComplete="one-time-code"
                      pattern="[0-9]{6}"
                      maxLength={6}
                      placeholder="• • • • • •"
                      value={otp}
                      onChange={(e) =>
                        setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))
                      }
                      disabled={busy}
                      required
                    />
                  </div>
                </div>

                {/* Remember + Resend row */}
                <div className="lp-remember-row">
                  <label className="lp-checkbox-label">
                    <input
                      type="checkbox"
                      checked={rememberDevice}
                      onChange={(e) => setRememberDevice(e.target.checked)}
                    />
                    Ghi nhớ thiết bị này
                  </label>
                  <button
                    type="button"
                    className="lp-resend-btn"
                    onClick={handleResend}
                    disabled={resendCooldown > 0 || busy}
                  >
                    <span className="material-symbols-outlined" style={{ fontSize: 14 }}>refresh</span>
                    Gửi lại mã{resendCooldown > 0 ? ` (${resendCooldown}s)` : ""}
                  </button>
                </div>

                {/* Primary CTA */}
                <button
                  type="submit"
                  className="lp-cta-btn"
                  disabled={busy || otp.length < 6}
                >
                  <span className="material-symbols-outlined" style={{ fontSize: 18 }}>
                    verified_user
                  </span>
                  {busy ? "Đang xác thực…" : "Xác thực OTP & Đăng nhập"}
                </button>
              </>
            )}
          </form>

          {/* ── SSO divider ──────────────────────────────────────────── */}
          <div className="lp-divider">
            <span>HOẶC TIẾP TỤC QUA</span>
          </div>

          <a
            href="#"
            className="lp-sso-btn"
            onClick={(e) => e.preventDefault()}
            aria-label="Đăng nhập qua UTH Single Sign-On"
          >
            <span className="material-symbols-outlined" style={{ fontSize: 18 }}>account_balance</span>
            UTH Single Sign-On (Cổng Đào Tạo UTH)
            <span className="material-symbols-outlined lp-sso-arrow">arrow_forward</span>
          </a>

          {/* Info note */}
          <div className="lp-note">
            <span className="material-symbols-outlined lp-note-icon">info</span>
            <p>
              Tài khoản sinh viên được đồng bộ tự động từ Cổng thông tin Đào
              tạo UTH. Nếu gặp sự cố đăng nhập, vui lòng liên hệ Trung tâm
              CNTT.
            </p>
          </div>
        </div>
      </main>

      {/* ── Footer ─────────────────────────────────────────────────────── */}
      <footer className="lp-footer">
        <span>
          © 2025 Trường Đại học Giao thông Vận tải TP.HCM (UTH) – Hệ thống
          Quản trị Thư viện Thông minh UTH-SeatSense
        </span>
        <nav className="lp-footer-links" aria-label="Điều hướng chân trang">
          <a href="#">Điều khoản dịch vụ</a>
          <a href="#">Bảo mật thông tin</a>
          <a href="#">Hướng dẫn sử dụng</a>
          <a href="#">Liên hệ Trung tâm CNTT</a>
        </nav>
      </footer>
    </div>
  );
}







