package vn.edu.uth.seatsense.data

import com.sun.net.httpserver.HttpServer
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.fail
import org.junit.Before
import org.junit.Test
import java.net.InetSocketAddress

class ApiClientTest {
    private lateinit var server: HttpServer
    private lateinit var baseUrl: String

    @Before
    fun setUp() {
        server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        server.start()
        baseUrl = "http://127.0.0.1:${server.address.port}/api/v1/"
    }

    @After
    fun tearDown() {
        server.stop(0)
    }

    @Test
    fun normalizeBaseUrl_addsTrailingSlashAndRejectsInvalidScheme() {
        assertEquals(
            "http://10.0.2.2:8000/api/v1/",
            ApiConfig.normalizeBaseUrl("http://10.0.2.2:8000/api/v1"),
        )
        try {
            ApiConfig.normalizeBaseUrl("ftp://example.com")
            fail("Expected invalid scheme to fail")
        } catch (_: IllegalArgumentException) {
            // expected
        }
    }

    @Test
    fun requestOtp_andLogin_workAgainstSharedAuthEndpoints() = runBlocking {
        var registerEmail: String? = null
        var registerAuthHeader: String? = null
        server.createContext("/api/v1/auth/register") { exchange ->
            registerAuthHeader = exchange.requestHeaders.getFirst("Authorization")
            val body = JSONObject(exchange.requestBody.bufferedReader().readText())
            registerEmail = body.getString("email")
            val payload = """{"status":"otp_sent"}""".toByteArray()
            exchange.sendResponseHeaders(202, payload.size.toLong())
            exchange.responseBody.use { it.write(payload) }
        }
        server.createContext("/api/v1/auth/login") { exchange ->
            val payload = """
                {
                  "access_token": "tok_test_123",
                  "token_type": "bearer",
                  "expires_at": "2026-11-28T05:00:00Z",
                  "user": {
                    "id": 7,
                    "email": "2151050123@ut.edu.vn",
                    "display_name": "Minh Anh",
                    "role": "student"
                  }
                }
            """.trimIndent().toByteArray()
            exchange.sendResponseHeaders(200, payload.size.toLong())
            exchange.responseBody.use { it.write(payload) }
        }

        val store = InMemoryTokenStore()
        val client = ApiClient(store, baseUrl)
        client.requestOtp("2151050123@ut.edu.vn")
        assertNull(registerAuthHeader)
        assertEquals("2151050123@ut.edu.vn", registerEmail)

        val result = client.login("2151050123@ut.edu.vn", "482910")
        assertEquals("tok_test_123", result.accessToken)
        assertEquals("Minh Anh", result.user.displayName)
        assertEquals("student", result.user.role)
    }

    @Test
    fun authenticatedRequests_sendBearerHeaderAndMapErrors() = runBlocking {
        var receivedAuth: String? = null
        server.createContext("/api/v1/auth/me") { exchange ->
            receivedAuth = exchange.requestHeaders.getFirst("Authorization")
            val payload = """
                {
                  "id": 7,
                  "email": "2151050123@ut.edu.vn",
                  "display_name": "Minh Anh",
                  "role": "student"
                }
            """.trimIndent().toByteArray()
            exchange.sendResponseHeaders(200, payload.size.toLong())
            exchange.responseBody.use { it.write(payload) }
        }
        server.createContext("/api/v1/auth/login") { exchange ->
            val payload = """
                {"error":{"code":"invalid_otp","message":"Invalid OTP"}}
            """.trimIndent().toByteArray()
            exchange.sendResponseHeaders(401, payload.size.toLong())
            exchange.responseBody.use { it.write(payload) }
        }

        val store = InMemoryTokenStore("secret_token")
        val client = ApiClient(store, baseUrl)
        val profile = client.me()
        assertEquals("Bearer secret_token", receivedAuth)
        assertEquals(7, profile.id)

        try {
            client.login("2151050123@ut.edu.vn", "000000")
            fail("Expected ApiFailure")
        } catch (failure: ApiFailure) {
            assertEquals(401, failure.statusCode)
            assertEquals("invalid_otp", failure.code)
        }
    }
}
