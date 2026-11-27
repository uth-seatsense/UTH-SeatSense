import { useMemo, useState } from "react";
import bookingsData from "../../mocks/bookings.json";

type Facility = (typeof bookingsData.facilities)[number];
type Room = Facility["rooms"][number];
type Slot = (typeof bookingsData.timeSlots)[number];
const amenities = ["Điều hòa trung tâm", "Màn hình TV 65\"", "Bảng kính viết bút", "Cổng HDMI / Type-C"];
const slotLabels: Record<string, string> = {
  "slot-1": "07:30 - 09:30", "slot-2": "09:30 - 11:30",
  "slot-3": "12:30 - 14:30", "slot-4": "14:30 - 16:30",
  "slot-5": "16:30 - 18:30", "slot-6": "18:30 - 20:30",
};
const bookedSlots: Record<string, string[]> = {
  "room-1-1": ["slot-2"], "room-1-2": ["slot-4"],
  "room-2-1": ["slot-2", "slot-5"], "room-2-2": ["slot-3"],
};
const mockRoomEquipment: Record<string, string[]> = {
  "room-1-1": ["Smart TV 65\" 4K UHD", "Bảng kính viết bút", "Trạm sạc đa năng bàn hộp", "Điều hòa trung tâm", "Cổng HDMI / Type-C"],
  "room-1-2": ["Smart TV 55\"", "Bảng kính viết bút", "Điều hòa trung tâm"],
  "room-2-1": ["Smart TV 75\" 4K UHD", "Bảng kính viết bút", "Cổng HDMI / Type-C"],
  "room-2-2": ["Smart TV 65\"", "Bảng kính viết bút", "Điều hòa trung tâm"],
};
const amenityKeywords: Record<string, string> = { "Điều hòa trung tâm": "điều hòa", "Màn hình TV 65\"": "smart tv", "Bảng kính viết bút": "bảng kính", "Cổng HDMI / Type-C": "hdmi" };
const roomCodes: Record<string, string> = {
  "room-1-1": "CS1-CD01", "room-1-2": "CS1-CD02",
  "room-2-1": "CS2-CD01", "room-2-2": "CS2-CD02",
};

function isoDate(date: Date) {
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
  return local.toISOString().slice(0, 10);
}
function formatDate(value: string) {
  if (!value) return "Chọn ngày";
  return new Intl.DateTimeFormat("vi-VN", { weekday: "long", day: "2-digit", month: "2-digit", year: "numeric" }).format(new Date(`${value}T12:00:00`));
}
function Icon({ children }: { children: string }) {
  return <span className="material-symbols-outlined" aria-hidden="true">{children}</span>;
}

export default function BookingPage() {
  const today = isoDate(new Date());
  const tomorrow = isoDate(new Date(Date.now() + 86_400_000));
  const [facilityId, setFacilityId] = useState<string>(bookingsData.facilities[0]?.id ?? "");
  const [date, setDate] = useState(today);
  const [roomId, setRoomId] = useState<string>(bookingsData.facilities[0]?.rooms[0]?.id ?? "");
  const [slotId, setSlotId] = useState("slot-3");
  const [amenityFilters, setAmenityFilters] = useState<string[]>([]);
  const [participants, setParticipants] = useState(6);
  const [purpose, setPurpose] = useState("Học nhóm Đồ án môn học");
  const [studentId, setStudentId] = useState("");
  const [message, setMessage] = useState("");
  const facility = bookingsData.facilities.find((item: Facility) => item.id === facilityId) ?? bookingsData.facilities[0];
  const rooms = facility?.rooms ?? [];
  const selectedRoom = rooms.find((item: Room) => item.id === roomId);
  const selectedSlot = bookingsData.timeSlots.find((item: Slot) => item.id === slotId);
  const filteredRooms = useMemo(() => rooms.filter((room: Room) => amenityFilters.every((filter) => (mockRoomEquipment[room.id] ?? room.equipment).some((item) => item.toLowerCase().includes(amenityKeywords[filter] ?? filter.toLowerCase())))), [rooms, amenityFilters]);

  function chooseFacility(id: string) {
    const next = bookingsData.facilities.find((item: Facility) => item.id === id);
    setFacilityId(id);
    setRoomId(next?.rooms[0]?.id ?? "");
    setSlotId("");
  }
  function toggleAmenity(item: string) {
    setAmenityFilters((current) => current.includes(item) ? current.filter((value) => value !== item) : [...current, item]);
  }
  function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!selectedRoom || !slotId || !studentId.trim()) {
      setMessage("Vui lòng chọn phòng, khung giờ và nhập MSSV người đặt.");
      return;
    }
    setMessage("Đã ghi nhận phiếu đặt phòng mẫu. Chưa gửi dữ liệu lên máy chủ.");
  }

  return (
    <div className="booking-shell">
      <aside className="booking-sidebar">
        <a className="booking-brand" href="/dashboard">
          <span className="booking-brand-mark"><Icon>school</Icon></span>
          <span><strong>UTH-SeatSense</strong><small>Đại học Giao thông Vận tải</small></span>
        </a>
        <nav className="booking-side-nav" aria-label="Điều hướng chính">
          <a href="/dashboard"><Icon>dashboard</Icon>Tổng quan</a>
          <a className="active" href="/booking" aria-current="page"><Icon>meeting_room</Icon>Đặt phòng học</a>
          <a href="/my-bookings"><Icon>history</Icon>Lịch đặt</a>
        </nav>
        <nav className="booking-side-bottom" aria-label="Hỗ trợ">
          <a href="#help"><Icon>help</Icon>Hỗ trợ &amp; Hướng dẫn</a>
          <a href="#settings"><Icon>settings</Icon>Cài đặt hệ thống</a>
        </nav>
      </aside>

      <div className="booking-workspace">
        <header className="booking-topbar">
          <label className="booking-search"><Icon>search</Icon><input aria-label="Tìm phòng" placeholder="Tìm theo tên phòng, tầng, thiết bị..." /></label>
          <button className="booking-tool-button" type="button"><Icon>map</Icon>Sơ đồ trường</button>
          <a className="booking-portal" href="https://portal.ut.edu.vn" target="_blank" rel="noreferrer"><Icon>school</Icon>Cổng Portal UTH<Icon>open_in_new</Icon></a>
          <button className="booking-bell" aria-label="Thông báo" type="button"><Icon>notifications</Icon><i /></button>
        </header>

        <main className="booking-content">
          <header className="booking-page-heading">
            <label className="booking-campus-select"><span>Cơ sở</span><select value={facilityId} onChange={(event) => chooseFacility(event.target.value)}>{bookingsData.facilities.map((item: Facility) => <option value={item.id} key={item.id}>{item.code}</option>)}</select></label>
            <h1>{facility?.code ?? "Thư viện"} - Đặt &amp; Quản lý Phòng Chuyên Đề</h1>
            <span className="booking-room-count"><i />{rooms.length} Phòng Chuyên đề</span>
            <p>Khu vực phòng học nhóm và nghiên cứu chuyên đề. Chọn phòng và ca còn trống để tạo phiếu đặt.</p>
          </header>

          <section className="booking-filter-panel" aria-label="Bộ lọc phòng">
            <div className="booking-filter-main">
              <div className="booking-filter-block booking-date-block">
                <label className="booking-filter-label"><Icon>calendar_month</Icon> Chọn ngày học</label>
                <div className="booking-date-control">
                  <button className={date === today ? "chosen" : ""} type="button" onClick={() => setDate(today)}>Hôm nay {new Date(`${today}T12:00:00`).toLocaleDateString("vi-VN")}</button>
                  <button className={date === tomorrow ? "chosen" : ""} type="button" onClick={() => setDate(tomorrow)}>Ngày mai {new Date(`${tomorrow}T12:00:00`).toLocaleDateString("vi-VN", { day: "2-digit", month: "2-digit" })}</button>
                  <label className="booking-calendar-button" aria-label="Chọn ngày khác"><Icon>edit_calendar</Icon><input type="date" min={today} value={date} onChange={(event) => setDate(event.target.value)} /></label>
                </div>
              </div>
              <label className="booking-capacity booking-filter-block"><span className="booking-filter-label"><Icon>groups</Icon> Sức chứa phòng</span><select><option>Tất cả phòng chuyên đề</option><option>8 người trở lên</option><option>10 người trở lên</option></select></label>
            </div>
            <div className="booking-amenities">
              <strong><Icon>devices</Icon> Thiết bị cần thiết:</strong>
              {amenities.map((item, index) => <label className={`booking-amenity ${amenityFilters.includes(item) ? "selected" : ""}`} key={item}><input type="checkbox" checked={amenityFilters.includes(item)} onChange={() => toggleAmenity(item)} /><span className="booking-check">{amenityFilters.includes(item) ? "✓" : ""}</span>{item}</label>)}
            </div>
          </section>

          <div className="booking-columns">
            <section className="booking-room-list" aria-label="Danh sách phòng">
              {filteredRooms.map((room: Room, index: number) => {
                const isSelected = room.id === selectedRoom?.id;
                const unavailable = bookedSlots[room.id] ?? [];
                return <article className={`booking-room-card ${isSelected ? "selected" : ""}`} key={room.id}>
                  <div className="booking-room-summary">
                    <span className={`booking-room-code ${index % 2 ? "blue" : ""}`}><small>MÃ PHÒNG</small><strong>{room.id.endsWith("1") ? "CD-01" : "CD-02"}</strong></span>
                    <div className="booking-room-main"><div className="booking-room-title"><h2>{room.name}</h2><code>{roomCodes[room.id] ?? room.id}</code></div>
                      <span className={`booking-occupancy ${isSelected ? "busy" : "free"}`}><i />{isSelected ? "Đang có nhóm sử dụng (6/" + room.capacity + " người)" : `Đang trống - Sẵn sàng sử dụng`}</span>
                      <p><Icon>groups</Icon> Sức chứa tối đa: <b>{room.capacity} người</b> (phù hợp nhóm học tập)</p>
                      <p><Icon>location_on</Icon> Phòng B301A (Tầng 3) <span>•</span> {facility?.code}</p>
                    </div>
                    <span className="booking-open-slots"><i />Còn {bookingsData.timeSlots.length - unavailable.length} ca trống hôm nay</span>
                  </div>
                  <div className="booking-equipment">{(mockRoomEquipment[room.id] ?? room.equipment).map((item: string, i: number) => <span key={item}><Icon>{i === 0 ? "tv" : i === 1 ? "draw" : "devices"}</Icon>{item}</span>)}</div>
                  <div className="booking-slot-section"><div className="booking-slot-heading"><strong>Lịch trống chi tiết các khung giờ ({date.slice(8, 10)}/{date.slice(5, 7)}/{date.slice(0, 4)}):</strong><span>{isSelected && slotId ? `Đang chọn: ${room.name} • ${slotLabels[slotId]}` : "Bấm vào khung giờ để chọn"}</span></div>
                    <div className="booking-slots">{bookingsData.timeSlots.slice(0, 5).map((slot: Slot, slotIndex: number) => {
                      const past = slotIndex === 0;
                      const busy = unavailable.includes(slot.id);
                      const active = isSelected && slotId === slot.id;
                      return <button key={slot.id} type="button" className={`booking-slot ${past ? "past" : busy ? "busy" : active ? "active" : "available"}`} disabled={past || busy} onClick={() => { setRoomId(room.id); setSlotId(slot.id); setMessage(""); }}><b>{slotLabels[slot.id] ?? `${slot.startTime} - ${slot.endTime}`}</b><small>{past ? "Đã hoàn tất" : busy ? "Đang sử dụng" : active ? "Đang chọn" : "Trống (Đặt ngay)"}</small></button>;
                    })}</div>
                  </div>
                </article>;
              })}
              {filteredRooms.length === 0 && <div className="booking-empty">Không có phòng phù hợp thiết bị đã chọn.</div>}
            </section>

            <aside className="booking-reservation-panel">
              <header><Icon>confirmation_number</Icon><h2>Thông tin phiếu đặt phòng</h2><span>Bước<br />1/2</span></header>
              <form onSubmit={submit}>
                <div className="booking-selected-card"><div className="booking-selected-top"><div><small>{facility?.code} • PHÒNG ĐÃ CHỌN</small><strong>{selectedRoom?.name ?? "Chọn phòng"} ({roomCodes[selectedRoom?.id ?? ""] ?? "—"})</strong></div><code>{roomCodes[selectedRoom?.id ?? ""] ?? "—"}</code></div><p>Phòng B301A • Thư viện Võ Oanh (Sức chứa tối đa: {selectedRoom?.capacity ?? "—"})</p><div className="booking-selected-fields"><label>Đổi phòng<select value={roomId} onChange={(event) => { setRoomId(event.target.value); setSlotId(""); }}><option value="">Chọn phòng</option>{rooms.map((room: Room) => <option key={room.id} value={room.id}>{room.name}</option>)}</select></label><label>Khung giờ<select value={slotId} onChange={(event) => setSlotId(event.target.value)}><option value="">Chọn ca</option>{bookingsData.timeSlots.filter((slot: Slot) => !(bookedSlots[selectedRoom?.id ?? ""] ?? []).includes(slot.id)).map((slot: Slot) => <option key={slot.id} value={slot.id}>{slotLabels[slot.id]}</option>)}</select></label></div><p className="booking-date-summary"><Icon>calendar_month</Icon>Ngày sử dụng: <b>{formatDate(date)}</b></p></div>
                  <label className="booking-form-label">Mục đích sử dụng phòng chuyên đề <em>* Bắt buộc</em><select value={purpose} onChange={(event) => setPurpose(event.target.value)}><option>Học nhóm Đồ án môn học</option><option>Nghiên cứu tài liệu</option><option>Thảo luận nhóm</option><option>Khác</option></select></label>
                  <label className="booking-form-label">Số lượng sinh viên tham gia <small>Quy định: 2 - {selectedRoom?.capacity ?? 10} người</small><span className="booking-number"><input type="number" min={2} max={selectedRoom?.capacity ?? 10} value={participants} onChange={(event) => setParticipants(Number(event.target.value))} /><small>sinh viên</small></span></label>
                  <label className="booking-form-label">MSSV người đặt <em>* Bắt buộc</em><input value={studentId} onChange={(event) => setStudentId(event.target.value)} placeholder="Nhập MSSV..." required /></label>
                  <div className="booking-policy"><strong><Icon>gavel</Icon> Quy định Phòng Chuyên đề:</strong><ul><li>Trưởng nhóm quét mã QR mở cửa đúng giờ (trước tối đa 15 phút).</li><li>Đảm bảo số lượng tối thiểu theo quy định.</li><li>Tắt thiết bị điện tử sau khi sử dụng.</li></ul></div>
                  {message && <p className={message.startsWith("Đã ghi") ? "booking-success" : "booking-error"} role="status">{message}</p>}
                  <button className="booking-submit" type="submit"><Icon>qr_code_2</Icon>Xác nhận &amp; Cấp mã mở phòng</button>
                  <p className="booking-mock-note">Dữ liệu minh họa • Chưa kết nối API</p>
              </form>
            </aside>
          </div>
        </main>
        <footer className="booking-footer">Hệ thống Quản lý Không gian Thư viện Thông minh UTH-SeatSense © 2024 Trường Đại học Giao thông Vận tải TP.HCM.</footer>
      </div>
    </div>
  );
}



