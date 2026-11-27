package vn.edu.uth.seatsense

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.journeyapps.barcodescanner.ScanContract
import com.journeyapps.barcodescanner.ScanOptions
import vn.edu.uth.seatsense.data.ApiClient
import vn.edu.uth.seatsense.data.ApiConfig
import vn.edu.uth.seatsense.data.TokenStore
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
        val initialBaseUrl = tokenStore.readApiBaseUrl() ?: ApiConfig.defaultBaseUrl()
        val api = ApiClient(tokenStore, initialBaseUrl)
        setContent {
            SeatSenseApp(
                api = api,
                tokenStore = tokenStore,
                onSaveApiBaseUrl = { updated -> tokenStore.writeApiBaseUrl(updated) },
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
