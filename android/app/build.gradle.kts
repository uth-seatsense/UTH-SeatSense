import java.util.Properties

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

val localProperties = Properties().apply {
    val file = rootProject.file("local.properties")
    if (file.isFile) {
        file.inputStream().use(::load)
    }
}

val rawApiBaseUrl = providers.gradleProperty("seatsenseApiBaseUrl")
    .orElse(
        providers.provider {
            localProperties.getProperty("seatsense.api.base.url")
        },
    )
    .orElse(providers.environmentVariable("SEATSENSE_API_BASE_URL"))
    .orElse("http://10.0.2.2:8000/api/v1/")
    .get()
    .trim()

val normalizedApiBaseUrl = (if (rawApiBaseUrl.endsWith("/")) rawApiBaseUrl else "$rawApiBaseUrl/")
    .replace("\\", "\\\\")
    .replace("\"", "\\\"")

android {
    namespace = "vn.edu.uth.seatsense"
    compileSdk = 35

    defaultConfig {
        applicationId = "vn.edu.uth.seatsense"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "0.1.0"
        buildConfigField("String", "API_BASE_URL", "\"$normalizedApiBaseUrl\"")
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    testOptions {
        unitTests.isReturnDefaultValues = true
    }
}

dependencies {
    implementation(platform("androidx.compose:compose-bom:2025.05.01"))
    implementation("androidx.activity:activity-compose:1.10.1")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.9.0")
    implementation("com.journeyapps:zxing-android-embedded:4.3.0")

    debugImplementation("androidx.compose.ui:ui-tooling")
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.json:json:20240303")
}
