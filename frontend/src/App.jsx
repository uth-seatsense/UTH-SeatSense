export default function App() {
  return (
    <main className="page">
      <section className="welcome-card" aria-labelledby="page-title">
        <p className="eyebrow">University of Transport Ho Chi Minh City</p>
        <h1 id="page-title">UTH-SeatSense</h1>
        <p className="description">
          Nền tảng khung quản lý phòng học và theo dõi tình trạng chỗ ngồi.
        </p>
        <span className="status">
          <span className="status-dot" aria-hidden="true" />
          Giao diện khởi tạo sẵn sàng
        </span>
      </section>
    </main>
  );
}
