package vn.edu.uth.seatsense

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.journeyapps.barcodescanner.ScanContract
import com.journeyapps.barcodescanner.ScanOptions
import vn.edu.uth.seatsense.data.SeatSenseApi
import vn.edu.uth.seatsense.security.TokenStore
import vn.edu.uth.seatsense.ui.SeatSenseApp

class MainActivity : ComponentActivity() {
    private var scanCallback: ((String) -> Unit)? = null
    private val scanLauncher = registerForActivityResult(ScanContract()) { result ->
        result.contents?.let { scanCallback?.invoke(it) }
        scanCallback = null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val tokenStore = TokenStore(applicationContext)
        val api = SeatSenseApi(tokenStore)
        setContent {
            SeatSenseApp(
                api = api,
                tokenStore = tokenStore,
                onScanQr = { callback ->
                    scanCallback = callback
                    scanLauncher.launch(
                        ScanOptions()
                            .setDesiredBarcodeFormats(ScanOptions.QR_CODE)
                            .setPrompt("Quét mã QR check-in")
                            .setBeepEnabled(false)
                            .setOrientationLocked(true),
                    )
                },
            )
        }
    }
}
