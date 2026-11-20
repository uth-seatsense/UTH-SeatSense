export function parseCheckInQr(value) {
  let payload;
  try {
    payload = JSON.parse(value);
  } catch {
    throw new Error("Mã QR không đúng định dạng JSON của SeatSense.");
  }
  if (
    !payload ||
    !Number.isInteger(payload.booking_id) ||
    payload.booking_id <= 0 ||
    typeof payload.qr_token !== "string" ||
    payload.qr_token.trim() === ""
  ) {
    throw new Error("Mã QR thiếu mã lượt đặt hoặc token check-in.");
  }
  return {
    bookingId: payload.booking_id,
    qrToken: payload.qr_token,
  };
}
