package vn.edu.uth.seatsense.data

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import java.io.IOException
import java.security.GeneralSecurityException
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

/**
 * Abstraction for storing the active OTP bearer token so callers and tests
 * do not depend directly on Android Keystore internals.
 */
interface SessionTokenStore {
    fun read(): String?
    fun write(token: String, persist: Boolean = true)
    fun clear()
}

/**
 * Lightweight in-memory [SessionTokenStore] for unit tests and Compose previews.
 */
class InMemoryTokenStore(initialToken: String? = null) : SessionTokenStore {
    @Volatile
    private var token: String? = initialToken

    override fun read(): String? = token

    override fun write(token: String, persist: Boolean) {
        this.token = token
    }

    override fun clear() {
        token = null
    }
}

/**
 * Secure session token storage backed by AES-GCM encryption in Android Keystore.
 * Supports session-only storage when "remember device" is unchecked.
 */
class TokenStore(context: Context) : SessionTokenStore {
    private val preferences =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    @Volatile
    private var sessionToken: String? = null

    @Throws(GeneralSecurityException::class, IOException::class)
    override fun read(): String? {
        sessionToken?.let { return it }
        val encrypted = preferences.getString(TOKEN_KEY, null) ?: return null
        val iv = preferences.getString(IV_KEY, null) ?: return null
        return try {
            val cipher = Cipher.getInstance(TRANSFORMATION)
            cipher.init(
                Cipher.DECRYPT_MODE,
                getOrCreateKey(),
                GCMParameterSpec(TAG_LENGTH_BITS, Base64.decode(iv, Base64.NO_WRAP)),
            )
            val cleartext = cipher.doFinal(Base64.decode(encrypted, Base64.NO_WRAP))
            cleartext.toString(Charsets.UTF_8).also { sessionToken = it }
        } catch (error: GeneralSecurityException) {
            clearPersistedToken()
            throw error
        } catch (_: IllegalArgumentException) {
            clearPersistedToken()
            null
        }
    }

    @Throws(GeneralSecurityException::class, IOException::class)
    override fun write(token: String, persist: Boolean) {
        sessionToken = token
        if (!persist) {
            clearPersistedToken()
            return
        }
        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.ENCRYPT_MODE, getOrCreateKey())
        val encrypted = Base64.encodeToString(
            cipher.doFinal(token.toByteArray(Charsets.UTF_8)),
            Base64.NO_WRAP,
        )
        val iv = Base64.encodeToString(cipher.iv, Base64.NO_WRAP)
        val saved = preferences.edit()
            .putString(TOKEN_KEY, encrypted)
            .putString(IV_KEY, iv)
            .commit()
        if (!saved) {
            throw IOException("Không thể lưu phiên đăng nhập an toàn trên thiết bị.")
        }
    }

    override fun clear() {
        sessionToken = null
        clearPersistedToken()
    }

    fun readApiBaseUrl(): String? =
        preferences.getString(API_BASE_URL_KEY, null)?.takeIf { it.isNotBlank() }

    fun writeApiBaseUrl(url: String?) {
        val trimmed = url?.trim().orEmpty()
        if (trimmed.isEmpty()) {
            preferences.edit().remove(API_BASE_URL_KEY).apply()
        } else {
            preferences.edit().putString(API_BASE_URL_KEY, trimmed).apply()
        }
    }

    private fun clearPersistedToken() {
        preferences.edit().remove(TOKEN_KEY).remove(IV_KEY).apply()
    }

    @Throws(GeneralSecurityException::class)
    private fun getOrCreateKey(): SecretKey {
        val keyStore = KeyStore.getInstance(ANDROID_KEY_STORE)
        keyStore.load(null)
        val existing = keyStore.getKey(KEY_ALIAS, null) as? SecretKey
        if (existing != null) {
            return existing
        }

        val generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, ANDROID_KEY_STORE)
        generator.init(
            KeyGenParameterSpec.Builder(
                KEY_ALIAS,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT,
            )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setRandomizedEncryptionRequired(true)
                .build(),
        )
        return generator.generateKey()
    }

    private companion object {
        const val PREFS_NAME = "seatsense_auth"
        const val ANDROID_KEY_STORE = "AndroidKeyStore"
        const val KEY_ALIAS = "seatsense_access_token"
        const val TOKEN_KEY = "token"
        const val IV_KEY = "iv"
        const val API_BASE_URL_KEY = "api_base_url"
        const val TAG_LENGTH_BITS = 128
        const val TRANSFORMATION = "AES/GCM/NoPadding"
    }
}
