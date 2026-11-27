package vn.edu.uth.seatsense.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONException
import org.json.JSONObject
import vn.edu.uth.seatsense.BuildConfig
import java.net.HttpURLConnection
import java.net.URL
import java.time.OffsetDateTime

data class UserProfile(
    val id: Int,
    val email: String,
    val displayName: String,
    val role: String,
)

data class LoginResult(
    val accessToken: String,
    val expiresAt: String,
    val user: UserProfile,
)

data class Room(
    val id: Int,
    val code: String,
    val name: String,
    val roomType: String,
    val capacity: Int,
    val campusCode: String?,
)

data class RoomOccupancy(
    val estimatedOccupancy: Int?,
    val isStale: Boolean,
)

data class Booking(
    val id: Int,
    val roomId: Int,
    val roomName: String,
    val participantCount: Int,
    val status: String,
    val startsAt: String,
    val endsAt: String,
)

data class CheckInToken(
    val bookingId: Int,
    val token: String,
    val expiresAt: String,
)

class ApiFailure(
    val statusCode: Int,
    val code: String,
    override val message: String,
) : Exception(message)

/**
 * Helpers for normalizing and validating the configured API base URL.
 */
object ApiConfig {
    fun defaultBaseUrl(): String = normalizeBaseUrl(BuildConfig.API_BASE_URL)

    fun normalizeBaseUrl(rawUrl: String): String {
        val trimmed = rawUrl.trim()
        require(trimmed.startsWith("http://") || trimmed.startsWith("https://")) {
            "Địa chỉ API phải bắt đầu bằng http:// hoặc https://"
        }
        val parsed = URL(trimmed)
        require(!parsed.host.isNullOrBlank()) {
            "Địa chỉ API không hợp lệ."
        }
        return if (trimmed.endsWith("/")) trimmed else "$trimmed/"
    }
}

/**
 * Shared HTTP client communicating with the UTH-SeatSense FastAPI backend.
 * Reads the default server endpoint from [BuildConfig.API_BASE_URL] and maps
 * backend error codes to Vietnamese user-facing messages.
 */
class ApiClient(
    private val tokenStore: SessionTokenStore,
    initialBaseUrl: String = ApiConfig.defaultBaseUrl(),
) {
    @Volatile
    private var baseUrl: String = ApiConfig.normalizeBaseUrl(initialBaseUrl)

    fun currentBaseUrl(): String = baseUrl

    fun updateBaseUrl(newUrl: String) {
        baseUrl = ApiConfig.normalizeBaseUrl(newUrl)
    }

    suspend fun requestOtp(email: String) {
        request(
            method = "POST",
            path = "auth/register",
            body = JSONObject().put("email", email.trim()),
            authenticated = false,
        )
    }

    suspend fun login(email: String, otp: String): LoginResult {
        val body = request(
            method = "POST",
            path = "auth/login",
            body = JSONObject()
                .put("email", email.trim())
                .put("otp", otp.trim()),
            authenticated = false,
        )
        val user = body.getJSONObject("user")
        return LoginResult(
            accessToken = body.getString("access_token"),
            expiresAt = body.optString("expires_at"),
            user = UserProfile(
                id = user.getInt("id"),
                email = user.getString("email"),
                displayName = user.getString("display_name"),
                role = user.getString("role"),
            ),
        )
    }

    suspend fun me(): UserProfile {
        val body = request("GET", "auth/me")
        return UserProfile(
            id = body.getInt("id"),
            email = body.getString("email"),
            displayName = body.getString("display_name"),
            role = body.getString("role"),
        )
    }

    suspend fun logout() {
        request("POST", "auth/logout")
    }

    suspend fun rooms(): List<Room> {
        val items = request("GET", "rooms").getJSONArray("items")
        return (0 until items.length()).map { index ->
            val item = items.getJSONObject(index)
            Room(
                id = item.getInt("id"),
                code = item.getString("code"),
                name = item.getString("name"),
                roomType = item.getString("room_type"),
                capacity = item.getInt("capacity"),
                campusCode = item.optionalString("campus_code"),
            )
        }
    }

    suspend fun occupancy(roomId: Int): RoomOccupancy {
        val body = request("GET", "occupancy/rooms/$roomId/latest")
        return RoomOccupancy(
            estimatedOccupancy = body.optionalInt("estimated_occupancy"),
            isStale = body.optBoolean("is_stale", false),
        )
    }

    suspend fun bookings(): List<Booking> {
        val items = request("GET", "bookings").getJSONArray("items")
        return (0 until items.length()).map { index ->
            val item = items.getJSONObject(index)
            Booking(
                id = item.getInt("id"),
                roomId = item.getInt("room_id"),
                roomName = item.getJSONObject("room").getString("name"),
                participantCount = item.getInt("participant_count"),
                status = item.getString("status"),
                startsAt = item.getString("starts_at"),
                endsAt = item.getString("ends_at"),
            )
        }
    }

    suspend fun createBooking(
        roomId: Int,
        startsAt: OffsetDateTime,
        endsAt: OffsetDateTime,
        participantCount: Int,
    ): Booking {
        val body = request(
            method = "POST",
            path = "bookings",
            body = JSONObject()
                .put("room_id", roomId)
                .put("starts_at", startsAt.toString())
                .put("ends_at", endsAt.toString())
                .put("participant_count", participantCount),
        )
        val room = body.getJSONObject("room")
        return Booking(
            id = body.getInt("id"),
            roomId = body.getInt("room_id"),
            roomName = room.getString("name"),
            participantCount = body.getInt("participant_count"),
            status = body.getString("status"),
            startsAt = body.getString("starts_at"),
            endsAt = body.getString("ends_at"),
        )
    }

    suspend fun cancelBooking(bookingId: Int) {
        request("DELETE", "bookings/$bookingId")
    }

    suspend fun createCheckInToken(bookingId: Int): CheckInToken {
        val body = request("POST", "bookings/$bookingId/check-in-token")
        return CheckInToken(
            bookingId = body.getInt("booking_id"),
            token = body.getString("qr_token"),
            expiresAt = body.getString("expires_at"),
        )
    }

    suspend fun checkIn(bookingId: Int, qrToken: String) {
        request(
            method = "POST",
            path = "check-in",
            body = JSONObject().put("booking_id", bookingId).put("qr_token", qrToken),
        )
    }

    private suspend fun request(
        method: String,
        path: String,
        body: JSONObject? = null,
        authenticated: Boolean = true,
    ): JSONObject = withContext(Dispatchers.IO) {
        val targetUrl = "${baseUrl.trimEnd('/')}/${path.trimStart('/')}"
        val connection = URL(targetUrl).openConnection() as HttpURLConnection
        try {
            connection.requestMethod = method
            connection.connectTimeout = 10_000
            connection.readTimeout = 15_000
            connection.setRequestProperty("Accept", "application/json")
            if (authenticated) {
                val token = tokenStore.read()
                    ?: throw ApiFailure(401, "unauthorized", ERROR_MESSAGES.getValue("unauthorized"))
                connection.setRequestProperty("Authorization", "Bearer $token")
            }
            if (body != null) {
                connection.doOutput = true
                connection.setRequestProperty("Content-Type", "application/json")
                connection.outputStream.use { output ->
                    output.write(body.toString().toByteArray(Charsets.UTF_8))
                }
            }

            val statusCode = connection.responseCode
            val stream = if (statusCode in 200..299) {
                connection.inputStream
            } else {
                connection.errorStream
            }
            val responseText = stream?.bufferedReader(Charsets.UTF_8)?.use { it.readText() }.orEmpty()
            val response = if (responseText.isBlank()) {
                JSONObject()
            } else {
                try {
                    JSONObject(responseText)
                } catch (_: JSONException) {
                    throw ApiFailure(
                        statusCode,
                        "invalid_response",
                        "Máy chủ trả về dữ liệu JSON không hợp lệ.",
                    )
                }
            }
            if (statusCode !in 200..299) {
                throw parseApiFailure(statusCode, response)
            }
            response
        } finally {
            connection.disconnect()
        }
    }

    private fun parseApiFailure(statusCode: Int, response: JSONObject): ApiFailure {
        val payload = response.optJSONObject("error") ?: response.optJSONObject("detail")
        val code = payload?.optString("code").orEmpty().ifBlank { "request_failed" }
        val serverMessage = payload?.optString("message").orEmpty()
        val message = ERROR_MESSAGES[code]
            ?: serverMessage.ifBlank { "Yêu cầu thất bại (HTTP $statusCode)." }
        return ApiFailure(
            statusCode = statusCode,
            code = code,
            message = message,
        )
    }

    private fun JSONObject.optionalString(key: String): String? =
        if (isNull(key)) null else optString(key).takeIf(String::isNotBlank)

    private fun JSONObject.optionalInt(key: String): Int? =
        if (isNull(key)) null else optInt(key)

    private companion object {
        val ERROR_MESSAGES = mapOf(
            "email_not_allowed" to "Email này chưa nằm trong danh sách được phép.",
            "otp_resend_too_soon" to "Vui lòng đợi trước khi yêu cầu mã OTP mới.",
            "invalid_otp" to "Thông tin xác thực không hợp lệ hoặc mã OTP đã hết hạn. Vui lòng kiểm tra lại email hoặc thử gửi lại mã mới.",
            "email_auth_unavailable" to "Đăng nhập OTP chưa được cấu hình trên máy chủ.",
            "otp_delivery_failed" to "Không gửi được email OTP. Vui lòng thử lại sau.",
            "account_inactive" to "Tài khoản hiện không hoạt động.",
            "unauthorized" to "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.",
            "validation_error" to "Dữ liệu nhập chưa hợp lệ. Vui lòng kiểm tra lại.",
        )
    }
}
