package vn.edu.uth.seatsense.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import vn.edu.uth.seatsense.R
import java.util.Locale

/**
 * Pure Kotlin validation and formatting helpers for the two-step OTP login flow.
 */
object OtpLoginHelper {
    const val OTP_TTL_SECONDS = 300
    const val RESEND_COOLDOWN_SECONDS = 60

    fun isValidEmail(raw: String): Boolean {
        val email = raw.trim()
        if (email.isEmpty() || email.contains(" ")) return false
        val atIndex = email.indexOf('@')
        if (atIndex <= 0 || atIndex != email.lastIndexOf('@')) return false
        val domain = email.substring(atIndex + 1)
        val dotIndex = domain.indexOf('.')
        return dotIndex > 0 && dotIndex < domain.length - 1
    }

    fun sanitizeOtp(raw: String): String =
        raw.filter(Char::isDigit).take(6)

    fun formatCountdown(seconds: Int): String {
        val clamped = seconds.coerceAtLeast(0)
        val minutes = clamped / 60
        val remaining = clamped % 60
        return "%02d:%02d".format(Locale.US, minutes, remaining)
    }
}

private object UthLoginColors {
    val PageBg = Color(0xFFF5FBF8)
    val Surface = Color(0xFFFFFFFF)
    val SurfaceSoft = Color(0xFFEFF5F2)
    val Primary = Color(0xFF006B5D)
    val PrimarySoft = Color(0x1A006B5D)
    val MintAccent = Color(0xFF56D5BE)
    val TextPrimary = Color(0xFF171D1B)
    val TextSecondary = Color(0xFF3D4946)
    val TextHint = Color(0xFF6C7A76)
    val Outline = Color(0xFFBCCAC5)
    val OutlineSoft = Color(0x99BCCAC5)
    val ErrorBg = Color(0xB3FFDAD6)
    val ErrorBorder = Color(0x33BA1A1A)
    val ErrorTitle = Color(0xFFBA1A1A)
    val ErrorBody = Color(0xFF93000A)
    val NoticeBg = Color(0xFFECFDF5)
    val NoticeBorder = Color(0x6656D5BE)
}

@Composable
fun LoginScreen(
    email: String,
    otp: String,
    otpRequested: Boolean,
    resendNonce: Int,
    rememberDevice: Boolean,
    busy: Boolean,
    error: String?,
    notice: String?,
    apiBaseUrl: String,
    onEmailChange: (String) -> Unit,
    onOtpChange: (String) -> Unit,
    onRememberDeviceChange: (Boolean) -> Unit,
    onRequestOtp: () -> Unit,
    onResendOtp: () -> Unit,
    onChangeEmail: () -> Unit,
    onLogin: (otpExpired: Boolean) -> Unit,
    onSsoClick: () -> Unit,
    onUpdateApiBaseUrl: (String) -> Unit,
) {
    var otpTtlSeconds by remember(otpRequested, resendNonce) {
        mutableIntStateOf(OtpLoginHelper.OTP_TTL_SECONDS)
    }
    var resendCooldownSeconds by remember(otpRequested, resendNonce) {
        mutableIntStateOf(OtpLoginHelper.RESEND_COOLDOWN_SECONDS)
    }
    var showServerDialog by remember { mutableStateOf(false) }

    LaunchedEffect(otpRequested, resendNonce) {
        if (!otpRequested) return@LaunchedEffect
        otpTtlSeconds = OtpLoginHelper.OTP_TTL_SECONDS
        resendCooldownSeconds = OtpLoginHelper.RESEND_COOLDOWN_SECONDS
        while (otpTtlSeconds > 0 || resendCooldownSeconds > 0) {
            delay(1_000L)
            if (otpTtlSeconds > 0) otpTtlSeconds -= 1
            if (resendCooldownSeconds > 0) resendCooldownSeconds -= 1
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(UthLoginColors.PageBg)
            .verticalScroll(rememberScrollState())
            .imePadding()
            .padding(bottom = 28.dp),
    ) {
        HeroHeader(onOpenServerConfig = { showServerDialog = true })

        Column(
            modifier = Modifier
                .fillMaxWidth()
                .offset(y = (-12).dp)
                .padding(horizontal = 16.dp),
        ) {
            // Form title
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Image(
                    painter = painterResource(R.drawable.ic_login),
                    contentDescription = null,
                    modifier = Modifier.size(16.dp),
                )
                Text(
                    text = "Đăng nhập sinh viên",
                    color = UthLoginColors.TextPrimary,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    lineHeight = 26.sp,
                )
            }
            Spacer(Modifier.height(2.dp))
            Text(
                text = "Xác thực mã OTP hoặc sử dụng tài khoản Cổng Đào Tạo",
                color = UthLoginColors.TextSecondary,
                fontSize = 12.sp,
                fontWeight = FontWeight.Medium,
                lineHeight = 16.sp,
            )

            Spacer(Modifier.height(16.dp))

            if (!error.isNullOrBlank()) {
                ErrorBanner(message = error)
                Spacer(Modifier.height(14.dp))
            }

            if (!notice.isNullOrBlank()) {
                NoticeBanner(message = notice)
                Spacer(Modifier.height(14.dp))
            }

            // Step 1: University email
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = "Email trường (@ut.edu.vn)",
                    color = UthLoginColors.TextSecondary,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold,
                )
                Text(
                    text = "VD: 2151050123@ut.edu.vn",
                    color = UthLoginColors.TextHint,
                    fontSize = 11.sp,
                )
            }
            Spacer(Modifier.height(6.dp))

            EmailInputBox(
                email = email,
                otpRequested = otpRequested,
                busy = busy,
                onEmailChange = onEmailChange,
                onRequestOtp = onRequestOtp,
                onChangeEmail = onChangeEmail,
            )

            Spacer(Modifier.height(6.dp))
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(5.dp),
            ) {
                Image(
                    painter = painterResource(R.drawable.ic_info_sm),
                    contentDescription = null,
                    modifier = Modifier.size(11.dp),
                )
                Text(
                    text = "Mã OTP gồm 6 chữ số sẽ được gửi về hộp thư sinh viên",
                    color = UthLoginColors.TextHint,
                    fontSize = 11.sp,
                    lineHeight = 16.sp,
                )
            }

            // Step 2: 6-digit OTP verification
            if (otpRequested) {
                Spacer(Modifier.height(18.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(
                        text = "Mã xác thực OTP (6 chữ số)",
                        color = UthLoginColors.TextSecondary,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold,
                    )
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(4.dp),
                    ) {
                        Image(
                            painter = painterResource(R.drawable.ic_timer),
                            contentDescription = null,
                            modifier = Modifier.size(11.dp),
                        )
                        Text(
                            text = if (otpTtlSeconds > 0) {
                                "Mã có hiệu lực trong ${OtpLoginHelper.formatCountdown(otpTtlSeconds)}"
                            } else {
                                "Mã OTP đã hết hạn"
                            },
                            color = if (otpTtlSeconds < 60) {
                                UthLoginColors.ErrorTitle
                            } else {
                                UthLoginColors.Primary
                            },
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Medium,
                        )
                    }
                }
                Spacer(Modifier.height(6.dp))

                OtpInputBox(
                    otp = otp,
                    busy = busy,
                    onOtpChange = { onOtpChange(OtpLoginHelper.sanitizeOtp(it)) },
                    onDone = {
                        if (!busy && otp.length == 6) {
                            onLogin(otpTtlSeconds <= 0)
                        }
                    },
                )

                Spacer(Modifier.height(12.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier
                            .clip(RoundedCornerShape(6.dp))
                            .clickable(enabled = !busy) {
                                onRememberDeviceChange(!rememberDevice)
                            }
                            .padding(vertical = 2.dp, horizontal = 2.dp),
                    ) {
                        RememberCheckbox(checked = rememberDevice)
                        Spacer(Modifier.width(8.dp))
                        Text(
                            text = "Ghi nhớ thiết bị này",
                            color = UthLoginColors.TextSecondary,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Medium,
                        )
                    }

                    TextButton(
                        onClick = onResendOtp,
                        enabled = !busy && resendCooldownSeconds == 0,
                        contentPadding = PaddingValues(horizontal = 8.dp, vertical = 2.dp),
                    ) {
                        Text(
                            text = if (resendCooldownSeconds > 0) {
                                "Gửi lại mã (${resendCooldownSeconds}s)"
                            } else {
                                "Gửi lại mã"
                            },
                            color = if (!busy && resendCooldownSeconds == 0) {
                                UthLoginColors.Primary
                            } else {
                                UthLoginColors.TextHint
                            },
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Medium,
                        )
                    }
                }

                Spacer(Modifier.height(14.dp))
                Button(
                    onClick = { onLogin(otpTtlSeconds <= 0) },
                    enabled = !busy && email.isNotBlank() && otp.length == 6,
                    shape = RoundedCornerShape(8.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = UthLoginColors.Primary,
                        contentColor = Color.White,
                        disabledContainerColor = UthLoginColors.Primary.copy(alpha = 0.45f),
                        disabledContentColor = Color.White.copy(alpha = 0.85f),
                    ),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(46.dp),
                ) {
                    if (busy) {
                        CircularProgressIndicator(
                            color = Color.White,
                            strokeWidth = 2.dp,
                            modifier = Modifier.size(16.dp),
                        )
                        Spacer(Modifier.width(8.dp))
                        Text(
                            text = "Đang xác thực...",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.SemiBold,
                        )
                    } else {
                        Image(
                            painter = painterResource(R.drawable.ic_verified),
                            contentDescription = null,
                            modifier = Modifier.size(15.dp),
                        )
                        Spacer(Modifier.width(8.dp))
                        Text(
                            text = "Xác thực OTP & Đăng nhập",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.SemiBold,
                        )
                    }
                }
            }

            Spacer(Modifier.height(20.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                HorizontalDivider(
                    modifier = Modifier.weight(1f),
                    color = UthLoginColors.Outline,
                    thickness = 1.dp,
                )
                Text(
                    text = "HOẶC TIẾP TỤC QUA",
                    color = UthLoginColors.TextHint,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.SemiBold,
                    letterSpacing = 0.55.sp,
                    modifier = Modifier.padding(horizontal = 12.dp),
                )
                HorizontalDivider(
                    modifier = Modifier.weight(1f),
                    color = UthLoginColors.Outline,
                    thickness = 1.dp,
                )
            }

            Spacer(Modifier.height(16.dp))
            OutlinedButton(
                onClick = onSsoClick,
                enabled = !busy,
                shape = RoundedCornerShape(8.dp),
                border = BorderStroke(1.dp, UthLoginColors.Outline),
                colors = ButtonDefaults.outlinedButtonColors(
                    containerColor = UthLoginColors.Surface,
                    contentColor = UthLoginColors.TextPrimary,
                ),
                contentPadding = PaddingValues(horizontal = 14.dp, vertical = 11.dp),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Box(
                    modifier = Modifier
                        .size(24.dp)
                        .clip(RoundedCornerShape(6.dp))
                        .background(UthLoginColors.PrimarySoft),
                    contentAlignment = Alignment.Center,
                ) {
                    Image(
                        painter = painterResource(R.drawable.ic_sso),
                        contentDescription = null,
                        modifier = Modifier.size(13.dp),
                    )
                }
                Spacer(Modifier.width(10.dp))
                Text(
                    text = "UTH Single Sign-On (Cổng Đào Tạo UTH)",
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.weight(1f, fill = false),
                )
                Spacer(Modifier.width(8.dp))
                Image(
                    painter = painterResource(R.drawable.ic_arrow),
                    contentDescription = null,
                    modifier = Modifier.size(10.dp),
                )
            }

            Spacer(Modifier.height(16.dp))
            Surface(
                color = UthLoginColors.SurfaceSoft,
                shape = RoundedCornerShape(12.dp),
                border = BorderStroke(1.dp, UthLoginColors.OutlineSoft),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Row(
                    modifier = Modifier.padding(13.dp),
                    horizontalArrangement = Arrangement.spacedBy(10.dp),
                    verticalAlignment = Alignment.Top,
                ) {
                    Image(
                        painter = painterResource(R.drawable.ic_info),
                        contentDescription = null,
                        modifier = Modifier
                            .padding(top = 2.dp)
                            .size(14.dp),
                    )
                    Text(
                        text = "Tài khoản sinh viên được đồng bộ tự động từ Cổng thông tin Đào tạo UTH. Nếu gặp sự cố đăng nhập, vui lòng liên hệ Trung tâm CNTT.",
                        color = UthLoginColors.TextSecondary,
                        fontSize = 12.sp,
                        lineHeight = 19.sp,
                    )
                }
            }

            Spacer(Modifier.height(22.dp))
            HorizontalDivider(color = UthLoginColors.OutlineSoft, thickness = 1.dp)
            Spacer(Modifier.height(18.dp))
            Text(
                text = "© 2025 Trường Đại học Giao thông Vận tải TP.HCM",
                color = UthLoginColors.TextHint,
                fontSize = 11.sp,
                textAlign = TextAlign.Center,
                modifier = Modifier.fillMaxWidth(),
            )
        }
    }

    if (showServerDialog) {
        ServerConfigDialog(
            currentUrl = apiBaseUrl,
            onDismiss = { showServerDialog = false },
            onSave = { updated ->
                onUpdateApiBaseUrl(updated)
                showServerDialog = false
            },
        )
    }
}

@Composable
private fun HeroHeader(onOpenServerConfig: () -> Unit) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(208.dp),
    ) {
        Image(
            painter = painterResource(R.drawable.uth_campus_bg),
            contentDescription = "Trường Đại học Giao thông Vận tải TP.HCM",
            contentScale = ContentScale.Crop,
            modifier = Modifier.fillMaxSize(),
        )
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    Brush.verticalGradient(
                        colors = listOf(
                            Color(0xCC006B5D),
                            Color(0x99006B5D),
                            UthLoginColors.PageBg,
                        ),
                    ),
                ),
        )
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color(0x4DF5FBF8)),
        )

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 20.dp, vertical = 18.dp),
            verticalArrangement = Arrangement.SpaceBetween,
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Surface(
                    color = Color(0xCCFFFFFF),
                    shape = RoundedCornerShape(999.dp),
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 5.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                    ) {
                        Image(
                            painter = painterResource(R.drawable.ic_school),
                            contentDescription = null,
                            modifier = Modifier.size(width = 16.dp, height = 13.dp),
                        )
                        Text(
                            text = "ĐH GIAO THÔNG VẬN TẢI TP.HCM",
                            color = UthLoginColors.Primary,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.SemiBold,
                            letterSpacing = 0.25.sp,
                        )
                    }
                }

                Surface(
                    color = Color(0xB3FFFFFF),
                    shape = CircleShape,
                    modifier = Modifier
                        .size(32.dp)
                        .clickable(onClick = onOpenServerConfig),
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Image(
                            painter = painterResource(R.drawable.ic_lang),
                            contentDescription = "Cấu hình địa chỉ máy chủ API",
                            modifier = Modifier.size(14.dp),
                        )
                    }
                }
            }

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                Box(
                    modifier = Modifier
                        .size(36.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(UthLoginColors.Primary),
                    contentAlignment = Alignment.Center,
                ) {
                    Image(
                        painter = painterResource(R.drawable.ic_book),
                        contentDescription = null,
                        modifier = Modifier.size(width = 18.dp, height = 21.dp),
                    )
                }
                Column {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                    ) {
                        Text(
                            text = "Đăng nhập Cổng Sinh viên",
                            color = UthLoginColors.TextPrimary,
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                            letterSpacing = (-0.4).sp,
                        )
                        Box(
                            modifier = Modifier
                                .size(8.dp)
                                .clip(CircleShape)
                                .background(UthLoginColors.MintAccent),
                        )
                    }
                    Text(
                        text = "Hệ thống thông minh đặt chỗ & phòng tự học",
                        color = UthLoginColors.TextSecondary,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Medium,
                    )
                }
            }
        }
    }
}

@Composable
private fun ErrorBanner(message: String) {
    Surface(
        color = UthLoginColors.ErrorBg,
        shape = RoundedCornerShape(12.dp),
        border = BorderStroke(1.dp, UthLoginColors.ErrorBorder),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Row(
            modifier = Modifier.padding(15.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalAlignment = Alignment.Top,
        ) {
            Image(
                painter = painterResource(R.drawable.ic_error),
                contentDescription = null,
                modifier = Modifier
                    .padding(top = 1.dp)
                    .size(width = 17.dp, height = 19.dp),
            )
            Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                Text(
                    text = "Xác thực không thành công",
                    color = UthLoginColors.ErrorTitle,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold,
                )
                Text(
                    text = message,
                    color = UthLoginColors.ErrorBody,
                    fontSize = 12.sp,
                    lineHeight = 19.sp,
                )
            }
        }
    }
}

@Composable
private fun NoticeBanner(message: String) {
    Surface(
        color = UthLoginColors.NoticeBg,
        shape = RoundedCornerShape(12.dp),
        border = BorderStroke(1.dp, UthLoginColors.NoticeBorder),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Text(
            text = message,
            color = UthLoginColors.Primary,
            fontSize = 12.sp,
            fontWeight = FontWeight.Medium,
            lineHeight = 18.sp,
            modifier = Modifier.padding(horizontal = 14.dp, vertical = 12.dp),
        )
    }
}

@Composable
private fun EmailInputBox(
    email: String,
    otpRequested: Boolean,
    busy: Boolean,
    onEmailChange: (String) -> Unit,
    onRequestOtp: () -> Unit,
    onChangeEmail: () -> Unit,
) {
    Surface(
        color = UthLoginColors.Surface,
        shape = RoundedCornerShape(8.dp),
        border = BorderStroke(1.dp, UthLoginColors.Outline),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(start = 14.dp, end = 6.dp, top = 6.dp, bottom = 6.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Image(
                painter = painterResource(R.drawable.ic_mail),
                contentDescription = null,
                modifier = Modifier.size(width = 17.dp, height = 14.dp),
            )
            Spacer(Modifier.width(12.dp))
            Box(modifier = Modifier.weight(1f)) {
                if (email.isEmpty()) {
                    Text(
                        text = "masinhvien@ut.edu.vn",
                        color = UthLoginColors.TextHint,
                        fontSize = 14.sp,
                    )
                }
                BasicTextField(
                    value = email,
                    onValueChange = onEmailChange,
                    enabled = !busy && !otpRequested,
                    singleLine = true,
                    textStyle = TextStyle(
                        color = if (otpRequested) UthLoginColors.TextSecondary else UthLoginColors.TextPrimary,
                        fontSize = 14.sp,
                    ),
                    cursorBrush = SolidColor(UthLoginColors.Primary),
                    keyboardOptions = KeyboardOptions(
                        keyboardType = KeyboardType.Email,
                        imeAction = if (otpRequested) ImeAction.Next else ImeAction.Send,
                    ),
                    keyboardActions = KeyboardActions(
                        onSend = {
                            if (!busy && !otpRequested && email.isNotBlank()) {
                                onRequestOtp()
                            }
                        },
                    ),
                    modifier = Modifier.fillMaxWidth(),
                )
            }
            Spacer(Modifier.width(8.dp))
            if (!otpRequested) {
                Surface(
                    color = UthLoginColors.PrimarySoft,
                    shape = RoundedCornerShape(6.dp),
                    modifier = Modifier.clickable(
                        enabled = !busy && email.isNotBlank(),
                        onClick = onRequestOtp,
                    ),
                ) {
                    Text(
                        text = if (busy) "Đang gửi..." else "Gửi mã OTP",
                        color = if (!busy && email.isNotBlank()) {
                            UthLoginColors.Primary
                        } else {
                            UthLoginColors.TextHint
                        },
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold,
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 7.dp),
                    )
                }
            } else {
                Surface(
                    color = UthLoginColors.SurfaceSoft,
                    shape = RoundedCornerShape(6.dp),
                    modifier = Modifier.clickable(enabled = !busy, onClick = onChangeEmail),
                ) {
                    Text(
                        text = "Đổi email",
                        color = UthLoginColors.TextSecondary,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold,
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 7.dp),
                    )
                }
            }
        }
    }
}

@Composable
private fun OtpInputBox(
    otp: String,
    busy: Boolean,
    onOtpChange: (String) -> Unit,
    onDone: () -> Unit,
) {
    Surface(
        color = UthLoginColors.Surface,
        shape = RoundedCornerShape(8.dp),
        border = BorderStroke(1.dp, UthLoginColors.Outline),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 14.dp, vertical = 12.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Image(
                painter = painterResource(R.drawable.ic_otp),
                contentDescription = null,
                modifier = Modifier.size(width = 17.dp, height = 14.dp),
            )
            Box(
                modifier = Modifier
                    .weight(1f)
                    .padding(end = 17.dp),
                contentAlignment = Alignment.Center,
            ) {
                if (otp.isEmpty()) {
                    Text(
                        text = "• • • • • •",
                        color = UthLoginColors.TextHint,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.SemiBold,
                        letterSpacing = 5.sp,
                        textAlign = TextAlign.Center,
                    )
                }
                BasicTextField(
                    value = otp,
                    onValueChange = onOtpChange,
                    enabled = !busy,
                    singleLine = true,
                    textStyle = TextStyle(
                        color = UthLoginColors.TextPrimary,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.SemiBold,
                        letterSpacing = 5.6.sp,
                        textAlign = TextAlign.Center,
                    ),
                    cursorBrush = SolidColor(UthLoginColors.Primary),
                    keyboardOptions = KeyboardOptions(
                        keyboardType = KeyboardType.Number,
                        imeAction = ImeAction.Done,
                    ),
                    keyboardActions = KeyboardActions(onDone = { onDone() }),
                    modifier = Modifier.fillMaxWidth(),
                )
            }
        }
    }
}

@Composable
private fun RememberCheckbox(checked: Boolean) {
    Box(
        modifier = Modifier
            .size(18.dp)
            .clip(RoundedCornerShape(4.dp))
            .background(if (checked) UthLoginColors.Primary else UthLoginColors.Surface)
            .border(
                width = 1.dp,
                color = if (checked) UthLoginColors.Primary else UthLoginColors.Outline,
                shape = RoundedCornerShape(4.dp),
            ),
        contentAlignment = Alignment.Center,
    ) {
        if (checked) {
            Image(
                painter = painterResource(R.drawable.ic_check),
                contentDescription = null,
                modifier = Modifier.size(14.dp),
            )
        }
    }
}

@Composable
private fun ServerConfigDialog(
    currentUrl: String,
    onDismiss: () -> Unit,
    onSave: (String) -> Unit,
) {
    var draft by remember(currentUrl) { mutableStateOf(currentUrl) }
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Địa chỉ API Backend") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(
                    text = "Emulator mặc định dùng http://10.0.2.2:8000/api/v1/. Điện thoại thật cùng Wi-Fi đổi sang IP máy tính chạy Docker.",
                    fontSize = 12.sp,
                    color = UthLoginColors.TextSecondary,
                )
                OutlinedTextField(
                    value = draft,
                    onValueChange = { draft = it },
                    singleLine = true,
                    label = { Text("API Base URL") },
                    modifier = Modifier.fillMaxWidth(),
                )
            }
        },
        confirmButton = {
            Button(
                onClick = { onSave(draft) },
                colors = ButtonDefaults.buttonColors(containerColor = UthLoginColors.Primary),
            ) {
                Text("Lưu")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Đóng")
            }
        },
    )
}
