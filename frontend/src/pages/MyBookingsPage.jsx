import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { QRCodeSVG } from "qrcode.react";
import {
  cancelBooking,
  createCheckInToken,
  getBookings,
} from "../services/api.js";

const BOOKING_STATUS = {
  booked: "Đã đặt",
  checked_in: "Đã check-in",
  completed: "Đã hoàn thành",
  cancelled: "Đã hủy",
  no_show: "Không đến",
};

function formatDate(value) {
  return new Intl.DateTimeFormat("vi-VN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export default function MyBookingsPage() {
  const location = useLocation();
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busyBookingId, setBusyBookingId] = useState(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState(location.state?.notice ?? "");
  const [qr, setQr] = useState(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    async function loadBookings() {
      setLoading(true);
      setError("");
      try {
        const items = await getBookings({ signal: controller.signal });
        if (active) setBookings(items);
      } catch (loadError) {
        if (active && loadError.name !== "AbortError") {
          setError(loadError.message);
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    loadBookings();
    return () => {
      active = false;
      controller.abort();
    };
  }, [reloadKey]);

  async function handleCancel(booking) {
    if (!window.confirm(`Hủy lượt đặt phòng ${booking.room.name}?`)) return;
    setBusyBookingId(booking.id);
    setError("");
    setNotice("");
    try {
      await cancelBooking(booking.id);
      setNotice("Đã hủy lượt đặt.");
      setReloadKey((value) => value + 1);
    } catch (cancelError) {
      setError(cancelError.message);
    } finally {
      setBusyBookingId(null);
    }
  }

  async function handleCreateQr(booking) {
    setBusyBookingId(booking.id);
    setError("");
    setNotice("");
    try {
      const token = await createCheckInToken(booking.id);
      setQr({
        bookingId: token.booking_id,
        payload: JSON.stringify({
          booking_id: token.booking_id,
          qr_token: token.qr_token,
        }),
        expiresAt: token.expires_at,
      });
    } catch (qrError) {
      setError(qrError.message);
    } finally {
      setBusyBookingId(null);
    }
  }

  return (
    <main className="feature-page">
      <header className="feature-heading">
        <p className="eyebrow">Tài khoản của bạn</p>
        <h1>Lịch đặt của tôi</h1>
        <p>Chỉ bạn mới xem và quản lý được các lượt đặt của mình.</p>
      </header>

      <div className="feature-toolbar">
        <span aria-live="polite">
          {loading ? "Đang tải lịch đặt..." : `${bookings.length} lượt đặt`}
        </span>
        <button
          className="button button--secondary"
          disabled={loading}
          onClick={() => setReloadKey((value) => value + 1)}
          type="button"
        >
          Làm mới
        </button>
      </div>
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
      {!loading && !error && bookings.length === 0 && (
        <div className="empty-panel">
          <p>Bạn chưa có lượt đặt nào.</p>
          <Link className="button button--primary" to="/reservation">
            Đặt phòng
          </Link>
        </div>
      )}
      <section aria-label="Các lượt đặt" className="booking-list">
        {bookings.map((booking) => (
          <article className="feature-panel booking-card" key={booking.id}>
            <div className="booking-card__details">
              <div>
                <h2>{booking.room.name}</h2>
                <p>
                  {booking.room.code}
                  {booking.room.campus_code
                    ? ` · ${booking.room.campus_code}`
                    : ""}
                </p>
              </div>
              <span className={`status-tag status-tag--${booking.status}`}>
                {BOOKING_STATUS[booking.status] ?? booking.status}
              </span>
              <p>
                {formatDate(booking.starts_at)} – {formatDate(booking.ends_at)}
              </p>
              <p>Nhóm {booking.participant_count} người</p>
            </div>
            {booking.status === "booked" && (
              <div className="booking-card__actions">
                <button
                  className="button button--primary"
                  disabled={busyBookingId === booking.id}
                  onClick={() => handleCreateQr(booking)}
                  type="button"
                >
                  Tạo mã QR
                </button>
                <button
                  className="button button--secondary"
                  disabled={busyBookingId === booking.id}
                  onClick={() => handleCancel(booking)}
                  type="button"
                >
                  Hủy lượt đặt
                </button>
              </div>
            )}
          </article>
        ))}
      </section>

      {qr && (
        <div
          aria-labelledby="checkin-qr-title"
          aria-modal="true"
          className="dialog-backdrop"
          role="dialog"
        >
          <section className="feature-panel qr-dialog">
            <h2 id="checkin-qr-title">Mã QR check-in</h2>
            <p>Lượt đặt #{qr.bookingId}</p>
            <QRCodeSVG
              aria-label="Mã QR check-in"
              bgColor="#ffffff"
              fgColor="#002452"
              includeMargin
              size={240}
              value={qr.payload}
            />
            <p className="helper-text">
              Có hiệu lực đến {formatDate(qr.expiresAt)}. Không chia sẻ mã này
              với người khác.
            </p>
            <Link
              className="text-link"
              onClick={() => setQr(null)}
              to="/checkin"
            >
              Đi đến trang check-in
            </Link>
            <button
              className="button button--secondary"
              onClick={() => setQr(null)}
              type="button"
            >
              Đóng
            </button>
          </section>
        </div>
      )}
    </main>
  );
}
