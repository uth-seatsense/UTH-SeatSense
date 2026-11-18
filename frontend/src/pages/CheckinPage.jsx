import { useEffect, useRef, useState } from "react";
import { checkIn } from "../services/api.js";
import { parseCheckInQr } from "../services/checkin.js";

export default function CheckinPage() {
  const videoRef = useRef(null);
  const [qrValue, setQrValue] = useState("");
  const [scanning, setScanning] = useState(false);
  const [scanError, setScanError] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  useEffect(() => {
    if (!scanning) return undefined;
    let cancelled = false;
    let stream;
    let timer;
    const video = videoRef.current;

    async function startScanner() {
      const BarcodeDetector = globalThis.BarcodeDetector;
      if (!BarcodeDetector || !navigator.mediaDevices?.getUserMedia) {
        setScanError(
          "Trình duyệt chưa hỗ trợ quét QR bằng camera. Hãy dùng chức năng quét của điện thoại rồi dán nội dung mã vào ô bên dưới.",
        );
        setScanning(false);
        return;
      }

      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: { ideal: "environment" } },
        });
        if (cancelled) {
          stream.getTracks().forEach((track) => track.stop());
          return;
        }
        video.srcObject = stream;
        await video.play();
        const detector = new BarcodeDetector({ formats: ["qr_code"] });

        async function detect() {
          if (cancelled) return;
          try {
            const codes = await detector.detect(video);
            if (codes.length > 0) {
              setQrValue(codes[0].rawValue);
              setScanError("");
              setScanning(false);
              return;
            }
            timer = window.setTimeout(detect, 350);
          } catch (scanFailure) {
            setScanError(`Không thể quét mã QR: ${scanFailure.message}`);
            setScanning(false);
          }
        }
        detect();
      } catch (cameraError) {
        setScanError(`Không mở được camera: ${cameraError.message}`);
        setScanning(false);
      }
    }

    startScanner();
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
      stream?.getTracks().forEach((track) => track.stop());
      if (video) video.srcObject = null;
    };
  }, [scanning]);

  async function submitCheckIn(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setResult(null);
    try {
      const payload = parseCheckInQr(qrValue.trim());
      const checkedIn = await checkIn(payload);
      setResult(checkedIn);
      setQrValue("");
    } catch (checkinError) {
      setError(checkinError.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="feature-page feature-page--narrow">
      <header className="feature-heading">
        <p className="eyebrow">Xác nhận lượt đặt</p>
        <h1>Check-in bằng QR</h1>
        <p>
          Quét mã QR của lượt đặt trên SeatSense hoặc dán nội dung QR do ứng
          dụng tạo. Mã chỉ dùng một lần và chỉ có hiệu lực trong khung giờ
          check-in.
        </p>
      </header>

      <section className="feature-panel feature-form">
        <button
          className="button button--secondary"
          disabled={scanning || busy}
          onClick={() => {
            setScanError("");
            setScanning(true);
          }}
          type="button"
        >
          {scanning ? "Đang mở camera..." : "Quét bằng camera"}
        </button>
        {scanning && (
          <video
            aria-label="Khung hình quét mã QR"
            autoPlay
            className="qr-camera"
            muted
            playsInline
            ref={videoRef}
          />
        )}
        {scanError && (
          <p className="feedback feedback--warning" role="status">
            {scanError}
          </p>
        )}
        <form className="feature-form" onSubmit={submitCheckIn}>
          <label className="form-field">
            <span>Nội dung mã QR</span>
            <textarea
              autoComplete="off"
              onChange={(event) => setQrValue(event.target.value)}
              placeholder='{"booking_id":123,"qr_token":"..."}'
              required
              rows={4}
              value={qrValue}
            />
          </label>
          {error && (
            <p className="feedback feedback--error" role="alert">
              {error}
            </p>
          )}
          {result && (
            <p className="feedback feedback--success" role="status">
              Check-in thành công cho lượt đặt #{result.booking_id} lúc{" "}
              {new Intl.DateTimeFormat("vi-VN", {
                dateStyle: "medium",
                timeStyle: "short",
              }).format(new Date(result.checked_in_at))}
              .
            </p>
          )}
          <button
            className="button button--primary"
            disabled={busy || qrValue.trim() === ""}
            type="submit"
          >
            {busy ? "Đang xác nhận..." : "Xác nhận check-in"}
          </button>
        </form>
      </section>
    </main>
  );
}
