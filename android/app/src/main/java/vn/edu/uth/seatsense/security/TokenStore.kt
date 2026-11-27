package vn.edu.uth.seatsense.security

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

class TokenStore(context: Context) {
    private val preferences =
        context.getSharedPreferences("seatsense_auth", Context.MODE_PRIVATE)

    @Throws(GeneralSecurityException::class, IOException::class)
    fun read(): String? {
        val encrypted = preferences.getString(TOKEN_KEY, null) ?: return null
        val iv = preferences.getString(IV_KEY, null) ?: return null
        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(
            Cipher.DECRYPT_MODE,
            getOrCreateKey(),
            GCMParameterSpec(TAG_LENGTH_BITS, Base64.decode(iv, Base64.NO_WRAP)),
        )
        val cleartext = cipher.doFinal(Base64.decode(encrypted, Base64.NO_WRAP))
        return cleartext.toString(Charsets.UTF_8)
    }

    @Throws(GeneralSecurityException::class, IOException::class)
    fun write(token: String) {
        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.ENCRYPT_MODE, getOrCreateKey())
        val encrypted = Base64.encodeToString(cipher.doFinal(token.toByteArray()), Base64.NO_WRAP)
        val iv = Base64.encodeToString(cipher.iv, Base64.NO_WRAP)
        val saved = preferences.edit()
            .putString(TOKEN_KEY, encrypted)
            .putString(IV_KEY, iv)
            .commit()
        if (!saved) {
            throw IOException("Could not save the sign-in session")
        }
    }

    fun clear() {
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
        const val ANDROID_KEY_STORE = "AndroidKeyStore"
        const val KEY_ALIAS = "seatsense_access_token"
        const val TOKEN_KEY = "token"
        const val IV_KEY = "iv"
        const val TAG_LENGTH_BITS = 128
        const val TRANSFORMATION = "AES/GCM/NoPadding"
    }
}
