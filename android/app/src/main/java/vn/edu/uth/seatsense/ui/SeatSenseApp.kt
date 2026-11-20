package vn.edu.uth.seatsense.ui

import android.graphics.Bitmap
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.ui.unit.dp
import com.google.zxing.BarcodeFormat
import com.google.zxing.qrcode.QRCodeWriter
import kotlinx.coroutines.launch
import org.json.JSONException
import org.json.JSONObject
import vn.edu.uth.seatsense.data.ApiFailure
import vn.edu.uth.seatsense.data.Booking
import vn.edu.uth.seatsense.data.Room
import vn.edu.uth.seatsense.data.RoomOccupancy
import vn.edu.uth.seatsense.data.SeatSenseApi
import vn.edu.uth.seatsense.data.UserProfile
import vn.edu.uth.seatsense.security.TokenStore
import java.io.IOException
import java.security.GeneralSecurityException
import java.time.DateTimeException
import java.time.OffsetDateTime

private enum class HomeTab(val label: String) {
    Occupancy("Chỗ trống"),
    Booking("Đặt phòng"),
    MyBookings("Lịch đặt"),
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SeatSenseApp(
    api: SeatSenseApi,
    tokenStore: TokenStore,
    onScanQr: ((String) -> Unit) -> Unit,
) {
    val scope = rememberCoroutineScope()
    var user by remember { mutableStateOf<UserProfile?>(null) }
    var email by remember { mutableStateOf("") }
    var otp by remember { mutableStateOf("") }
    var otpRequested by remember { mutableStateOf(false) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    var notice by remember { mutableStateOf<String?>(null) }
    var selectedTab by remember { mutableStateOf(HomeTab.Occupancy) }
    var rooms by remember { mutableStateOf<List<Room>>(emptyList()) }
    var bookings by remember { mutableStateOf<List<Booking>>(emptyList()) }
    val occupancies = remember { mutableStateMapOf<Int, RoomOccupancy?>() }
    var qrPayload by remember { mutableStateOf<String?>(null) }

    suspend fun refresh() {
        rooms = api.rooms()
        bookings = api.bookings()
        occupancies.clear()
        for (room in rooms) {
            try {
                occupancies[room.id] = api.occupancy(room.id)
            } catch (failure: ApiFailure) {
                if (failure.code == "occupancy_not_found") {
                    occupancies[room.id] = null
                } else {
                    throw failure
                }
            }
        }
    }

    fun execute(action: suspend () -> Unit) {
        scope.launch {
            busy = true
            error = null
            notice = null
            try {
                action()
            } catch (failure: ApiFailure) {
                error = failure.message
                if (failure.statusCode == 401) {
                    tokenStore.clear()
                    user = null
                }
            } catch (failure: IOException) {
                error = "Không kết nối được máy chủ. Hãy kiểm tra địa chỉ API và mạng."
            } catch (failure: GeneralSecurityException) {
                error = "Không thể đọc phiên đăng nhập an toàn trên thiết bị."
            } catch (failure: JSONException) {
                error = "Dữ liệu QR hoặc phản hồi API không hợp lệ."
            } catch (failure: DateTimeException) {
                error = "Ngày giờ không đúng định dạng ISO 8601 có múi giờ."
            } finally {
                busy = false
            }
        }
    }

    LaunchedEffect(Unit) {
        try {
            if (tokenStore.read() != null) {
                user = api.me()
                refresh()
            }
        } catch (failure: ApiFailure) {
            if (failure.statusCode == 401) {
                tokenStore.clear()
            } else {
                error = failure.message
            }
        } catch (failure: IOException) {
            error = "Không kết nối được máy chủ. Hãy kiểm tra địa chỉ API và mạng."
        } catch (failure: GeneralSecurityException) {
            error = "Không thể đọc phiên đăng nhập an toàn trên thiết bị."
        } catch (failure: JSONException) {
            error = "Máy chủ trả về dữ liệu không hợp lệ."
        }
    }

    if (user == null) {
        LoginPanel(
            email = email,
            otp = otp,
            otpRequested = otpRequested,
            busy = busy,
            error = error,
            notice = notice,
            onEmailChange = { email = it },
            onOtpChange = { otp = it },
            onRequestOtp = {
                execute {
                    api.requestOtp(email.trim())
                    otpRequested = true
                    notice = "Nếu email thuộc danh sách cho phép, mã xác minh sẽ được gửi."
                }
            },
            onLogin = {
                execute {
                    val result = api.login(email.trim(), otp.trim())
                    tokenStore.write(result.accessToken)
                    user = result.user
                    otpRequested = false
                    otp = ""
                    refresh()
                }
            },
        )
        return
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("UTH SeatSense") },
                actions = {
                    OutlinedButton(
                        onClick = {
                            execute {
                                api.logout()
                                tokenStore.clear()
                                user = null
                                bookings = emptyList()
                                rooms = emptyList()
                                occupancies.clear()
                            }
                        },
                        enabled = !busy,
                        modifier = Modifier.padding(end = 8.dp),
                    ) {
                        Text("Đăng xuất")
                    }
                },
            )
        },
        bottomBar = {
            NavigationBar {
                HomeTab.entries.forEach { tab ->
                    NavigationBarItem(
                        selected = selectedTab == tab,
                        onClick = { selectedTab = tab },
                        icon = {},
                        label = { Text(tab.label) },
                    )
                }
            }
        },
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = 16.dp),
        ) {
            Text(
                text = "Xin chào, ${user?.displayName.orEmpty()}",
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(vertical = 8.dp),
            )
            StatusMessages(error = error, notice = notice)
            if (busy) {
                CircularProgressIndicator(modifier = Modifier.align(Alignment.CenterHorizontally))
            }

            when (selectedTab) {
                HomeTab.Occupancy -> OccupancyPanel(
                    rooms = rooms,
                    occupancies = occupancies,
                    busy = busy,
                    onRefresh = { execute { refresh() } },
                )
                HomeTab.Booking -> BookingPanel(
                    rooms = rooms.filter { it.roomType == "topic_room" },
                    busy = busy,
                    onError = { error = it },
                    onCreate = { roomId, startsAt, endsAt, participants ->
                        execute {
                            api.createBooking(roomId, startsAt, endsAt, participants)
                            refresh()
                            selectedTab = HomeTab.MyBookings
                            notice = "Đặt phòng đã được xác nhận."
                        }
                    },
                )
                HomeTab.MyBookings -> MyBookingsPanel(
                    bookings = bookings,
                    busy = busy,
                    onRefresh = { execute { refresh() } },
                    onCancel = { bookingId ->
                        execute {
                            api.cancelBooking(bookingId)
                            refresh()
                            notice = "Đã hủy lượt đặt."
                        }
                    },
                    onShowQr = { bookingId ->
                        execute {
                            val token = api.createCheckInToken(bookingId)
                            qrPayload = JSONObject()
                                .put("booking_id", token.bookingId)
                                .put("qr_token", token.token)
                                .toString()
                        }
                    },
                    onScan = {
                        onScanQr { raw ->
                            execute {
                                val code = JSONObject(raw)
                                api.checkIn(
                                    bookingId = code.getInt("booking_id"),
                                    qrToken = code.getString("qr_token"),
                                )
                                refresh()
                                notice = "Check-in thành công."
                            }
                        }
                    },
                )
            }
        }
    }

    qrPayload?.let { payload ->
        QrDialog(
            payload = payload,
            onDismiss = { qrPayload = null },
        )
    }
}

@Composable
private fun LoginPanel(
    email: String,
    otp: String,
    otpRequested: Boolean,
    busy: Boolean,
    error: String?,
    notice: String?,
    onEmailChange: (String) -> Unit,
    onOtpChange: (String) -> Unit,
    onRequestOtp: () -> Unit,
    onLogin: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.Center,
    ) {
        Text("Đăng nhập bằng email", style = MaterialTheme.typography.headlineSmall)
        Spacer(Modifier.height(12.dp))
        Text("Mã OTP chỉ có hiệu lực trong thời gian giới hạn và chỉ dùng một lần.")
        Spacer(Modifier.height(16.dp))
        OutlinedTextField(
            value = email,
            onValueChange = onEmailChange,
            label = { Text("Email được cấp quyền") },
            enabled = !busy,
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
        )
        if (otpRequested) {
            Spacer(Modifier.height(12.dp))
            OutlinedTextField(
                value = otp,
                onValueChange = { value -> onOtpChange(value.filter(Char::isDigit).take(6)) },
                label = { Text("Mã OTP 6 chữ số") },
                enabled = !busy,
                singleLine = true,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.NumberPassword),
                modifier = Modifier.fillMaxWidth(),
            )
        }
        StatusMessages(error = error, notice = notice)
        Spacer(Modifier.height(16.dp))
        Button(
            onClick = if (otpRequested) onLogin else onRequestOtp,
            enabled = !busy && email.isNotBlank() && (!otpRequested || otp.length == 6),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(if (otpRequested) "Xác minh và đăng nhập" else "Gửi mã OTP")
        }
        if (otpRequested) {
            OutlinedButton(
                onClick = onRequestOtp,
                enabled = !busy,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text("Gửi lại mã")
            }
        }
    }
}

@Composable
private fun OccupancyPanel(
    rooms: List<Room>,
    occupancies: Map<Int, RoomOccupancy?>,
    busy: Boolean,
    onRefresh: () -> Unit,
) {
    Column(modifier = Modifier.fillMaxSize()) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text("Tình trạng phòng", style = MaterialTheme.typography.titleLarge)
            OutlinedButton(onClick = onRefresh, enabled = !busy) { Text("Làm mới") }
        }
        if (rooms.isEmpty() && !busy) {
            Text("Chưa có phòng đang hoạt động.")
        } else {
            LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                items(rooms, key = Room::id) { room ->
                    OccupancyCard(room, occupancies[room.id])
                }
            }
        }
    }
}

@Composable
private fun OccupancyCard(room: Room, occupancy: RoomOccupancy?) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(room.name, style = MaterialTheme.typography.titleMedium)
            Text("${room.code} · ${room.campusCode ?: "Chưa gán cơ sở"} · Sức chứa ${room.capacity}")
            when {
                occupancy == null -> Text("Chưa có dữ liệu chỗ trống.")
                occupancy.estimatedOccupancy == null -> Text("Chưa đủ dữ liệu để tính chỗ trống.")
                else -> {
                    val count = occupancy.estimatedOccupancy
                    val available = (room.capacity - count).coerceAtLeast(0)
                    Text("Đang sử dụng: $count · Chỗ trống: $available")
                    if (count > room.capacity) {
                        Text("Cảnh báo: số người vượt sức chứa.")
                    }
                    if (occupancy.isStale) {
                        Text("Cảnh báo: dữ liệu đã cũ.")
                    }
                }
            }
        }
    }
}

@Composable
private fun BookingPanel(
    rooms: List<Room>,
    busy: Boolean,
    onError: (String) -> Unit,
    onCreate: (Int, OffsetDateTime, OffsetDateTime, Int) -> Unit,
) {
    var selectedRoomId by remember(rooms) { mutableStateOf(rooms.firstOrNull()?.id) }
    var menuExpanded by remember { mutableStateOf(false) }
    val defaultStart = remember {
        OffsetDateTime.now().plusHours(1).withSecond(0).withNano(0).toString()
    }
    var startsAt by remember { mutableStateOf(defaultStart) }
    var endsAt by remember {
        mutableStateOf(
            OffsetDateTime.parse(defaultStart).plusMinutes(60).toString(),
        )
    }
    var participants by remember { mutableStateOf("2") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text("Đặt phòng chuyên đề", style = MaterialTheme.typography.titleLarge)
        if (rooms.isEmpty()) {
            Text("Hiện chưa có phòng chuyên đề đang hoạt động.")
            return@Column
        }
        OutlinedButton(onClick = { menuExpanded = true }, enabled = !busy) {
            Text(rooms.firstOrNull { it.id == selectedRoomId }?.name ?: "Chọn phòng")
        }
        androidx.compose.material3.DropdownMenu(
            expanded = menuExpanded,
            onDismissRequest = { menuExpanded = false },
        ) {
            rooms.forEach { room ->
                androidx.compose.material3.DropdownMenuItem(
                    text = { Text("${room.name} · ${room.code}") },
                    onClick = {
                        selectedRoomId = room.id
                        menuExpanded = false
                    },
                )
            }
        }
        OutlinedTextField(
            value = startsAt,
            onValueChange = { startsAt = it },
            label = { Text("Bắt đầu (ISO 8601, có múi giờ)") },
            enabled = !busy,
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
        )
        OutlinedTextField(
            value = endsAt,
            onValueChange = { endsAt = it },
            label = { Text("Kết thúc (ISO 8601, có múi giờ)") },
            enabled = !busy,
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
        )
        OutlinedTextField(
            value = participants,
            onValueChange = { participants = it.filter(Char::isDigit).take(1) },
            label = { Text("Số thành viên (2–6)") },
            enabled = !busy,
            singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth(),
        )
        Button(
            onClick = {
                val roomId = selectedRoomId
                val count = participants.toIntOrNull()
                if (roomId == null || count == null || count !in 2..6) {
                    onError("Chọn phòng và nhập nhóm từ 2 đến 6 người.")
                } else {
                    try {
                        onCreate(
                            roomId,
                            OffsetDateTime.parse(startsAt),
                            OffsetDateTime.parse(endsAt),
                            count,
                        )
                    } catch (_: DateTimeException) {
                        onError("Ngày giờ cần theo dạng ISO 8601 có múi giờ.")
                    }
                }
            },
            enabled = !busy,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text("Xác nhận đặt phòng")
        }
    }
}

@Composable
private fun MyBookingsPanel(
    bookings: List<Booking>,
    busy: Boolean,
    onRefresh: () -> Unit,
    onCancel: (Int) -> Unit,
    onShowQr: (Int) -> Unit,
    onScan: () -> Unit,
) {
    Column(modifier = Modifier.fillMaxSize()) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text("Lịch đặt của tôi", style = MaterialTheme.typography.titleLarge)
            OutlinedButton(onClick = onRefresh, enabled = !busy) { Text("Làm mới") }
        }
        OutlinedButton(
            onClick = onScan,
            enabled = !busy,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text("Quét QR check-in")
        }
        if (bookings.isEmpty()) {
            Text("Bạn chưa có lượt đặt nào.")
        } else {
            LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                items(bookings, key = Booking::id) { booking ->
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(
                            modifier = Modifier.padding(16.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp),
                        ) {
                            Text(booking.roomName, style = MaterialTheme.typography.titleMedium)
                            Text("${booking.startsAt} – ${booking.endsAt}")
                            Text("Nhóm ${booking.participantCount} người · ${booking.status}")
                            if (booking.status == "booked") {
                                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                    OutlinedButton(
                                        onClick = { onShowQr(booking.id) },
                                        enabled = !busy,
                                    ) {
                                        Text("Tạo mã QR")
                                    }
                                    OutlinedButton(
                                        onClick = { onCancel(booking.id) },
                                        enabled = !busy,
                                    ) {
                                        Text("Hủy")
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun QrDialog(payload: String, onDismiss: () -> Unit) {
    val bitmap = remember(payload) { qrBitmap(payload) }
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Mã QR check-in") },
        text = {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Image(
                    bitmap = bitmap.asImageBitmap(),
                    contentDescription = "Mã QR lượt đặt",
                    modifier = Modifier.size(240.dp),
                )
                Text("Mã chỉ dùng một lần và hết hạn sau thời gian check-in.")
            }
        },
        confirmButton = {
            Button(onClick = onDismiss) { Text("Đóng") }
        },
    )
}

@Composable
private fun StatusMessages(error: String?, notice: String?) {
    if (error != null) {
        Text(error, color = MaterialTheme.colorScheme.error)
    }
    if (notice != null) {
        Text(notice, color = MaterialTheme.colorScheme.primary)
    }
}

private fun qrBitmap(payload: String): Bitmap {
    val matrix = QRCodeWriter().encode(payload, BarcodeFormat.QR_CODE, 640, 640)
    return Bitmap.createBitmap(matrix.width, matrix.height, Bitmap.Config.ARGB_8888).apply {
        for (x in 0 until matrix.width) {
            for (y in 0 until matrix.height) {
                setPixel(
                    x,
                    y,
                    if (matrix[x, y]) android.graphics.Color.BLACK else android.graphics.Color.WHITE,
                )
            }
        }
    }
}
