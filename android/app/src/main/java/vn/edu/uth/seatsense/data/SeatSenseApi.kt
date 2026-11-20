package vn.edu.uth.seatsense.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONException
import org.json.JSONObject
import vn.edu.uth.seatsense.BuildConfig
import vn.edu.uth.seatsense.security.TokenStore
import java.io.IOException
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

class SeatSenseApi(
    private val tokenStore: TokenStore,
    private val baseUrl: String = BuildConfig.API_BASE_URL,
) {
    suspend fun requestOtp(email: String) {
        request(
            method = "POST",
            path = "auth/register",
            body = JSONObject().put("email", email),
            authenticated = false,
        )
    }

    suspend fun login(email: String, otp: String): LoginResult {
        val body = request(
            method = "POST",
            path = "auth/login",
            body = JSONObject().put("email", email).put("otp", otp),
            authenticated = false,
        )
        val user = body.getJSONObject("user")
        return LoginResult(
            accessToken = body.getString("access_token"),
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
        val connection = URL("${baseUrl.trimEnd('/')}/${path.trimStart('/')}")
            .openConnection() as HttpURLConnection
        try {
            connection.requestMethod = method
            connection.connectTimeout = 10_000
            connection.readTimeout = 15_000
            connection.setRequestProperty("Accept", "application/json")
            if (authenticated) {
                val token = tokenStore.read()
                    ?: throw ApiFailure(401, "unauthorized", "Please sign in again")
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
                    throw ApiFailure(statusCode, "invalid_response", "The server returned invalid JSON")
                }
            }
            if (statusCode !in 200..299) {
                val error = response.optJSONObject("error")
                throw ApiFailure(
                    statusCode = statusCode,
                    code = error?.optString("code").orEmpty().ifBlank { "request_failed" },
                    message = error?.optString("message").orEmpty().ifBlank {
                        "The request failed (HTTP $statusCode)"
                    },
                )
            }
            response
        } finally {
            connection.disconnect()
        }
    }

    private fun JSONObject.optionalString(key: String): String? =
        if (isNull(key)) null else optString(key).takeIf(String::isNotBlank)

    private fun JSONObject.optionalInt(key: String): Int? =
        if (isNull(key)) null else optInt(key)
}
