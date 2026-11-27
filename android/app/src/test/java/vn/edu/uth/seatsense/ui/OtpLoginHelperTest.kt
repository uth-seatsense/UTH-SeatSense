package vn.edu.uth.seatsense.ui

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class OtpLoginHelperTest {
    @Test
    fun isValidEmail_acceptsValidUniversityAndDomainAddresses() {
        assertTrue(OtpLoginHelper.isValidEmail("2151050123@ut.edu.vn"))
        assertTrue(OtpLoginHelper.isValidEmail("  sv@uth.edu.vn "))
        assertFalse(OtpLoginHelper.isValidEmail(""))
        assertFalse(OtpLoginHelper.isValidEmail("not-an-email"))
        assertFalse(OtpLoginHelper.isValidEmail("sv@localhost"))
        assertFalse(OtpLoginHelper.isValidEmail("sv @ut.edu.vn"))
    }

    @Test
    fun sanitizeOtp_keepsUpToSixDigitsOnly() {
        assertEquals("482910", OtpLoginHelper.sanitizeOtp("48-29a10 99"))
        assertEquals("123", OtpLoginHelper.sanitizeOtp("abc123"))
        assertEquals("", OtpLoginHelper.sanitizeOtp("abcdef"))
    }

    @Test
    fun formatCountdown_formatsMinutesAndSecondsSafely() {
        assertEquals("05:00", OtpLoginHelper.formatCountdown(300))
        assertEquals("02:48", OtpLoginHelper.formatCountdown(168))
        assertEquals("00:05", OtpLoginHelper.formatCountdown(5))
        assertEquals("00:00", OtpLoginHelper.formatCountdown(-10))
    }
}
