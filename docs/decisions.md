# Architecture decisions

## Initial service boundaries

- **Status:** Accepted for the project scaffold
- **Decision:** Keep the web UI, business API, and CV processing in separate
  service directories, with PostgreSQL as the shared persistence layer.
- **Reason:** The components have distinct responsibilities and runtime needs.
- **Follow-up:** Validate deployment, authentication, and inter-service
  communication requirements with the team.

## SEAT-17 CV output and counting semantics

- **Status:** Implemented in CV, pending team review.
- **Date:** 2026-10-30.
- **Decision:** Version the transport-neutral CV output as 1.0. Keep aggregate
  count records separate from local bbox debug records. Define the output
  before Backend implements ingestion; no HTTP endpoint is assumed yet.
- **Counting:** Visible person count is independent of cumulative line IN/OUT.
  Only estimate room occupancy when an initial value is explicitly configured.
  Clamp negative estimates to zero while flagging underflow.
- **Tracking:** Bottom-center anchors cross a finite normalized segment, with
  deadband, cooldown and stale-state expiry. Counters reset for each session.
- **Follow-up:** Backend ingestion, storage and UI are separate stages.

## SEAT-48 Frontend and native framework selection

- **Date:** 2026-11-10.
- **Status:** Approved by Uyên on 2026-11-10 for React + Vite web and Android
  native with Kotlin. The native build/runtime spike remains a follow-up; this
  approval does not claim that Kotlin or native QR/chart integrations were
  prototyped.
- **Scope:** Select the web framework and native-app approach. iOS is outside
  the current project scope.

| Candidate | Group experience / learning | QR and chart ecosystem | iOS build requirement | Code reuse | Docker fit |
|---|---|---|---|---|---|
| React + Vite (web) | Existing frontend, API client, pages and tests provide direct project experience; lowest migration cost. | Mature web choices exist (for example, Chart.js/ECharts and browser QR scanning with ZXing); no chart or QR package is selected in this repository yet. | Web build is platform-independent; no macOS needed. | Reuses the current React/JavaScript frontend. | Already builds with the existing Node/Vite Docker service; keep camera/CV outside Docker. |
| Vue + Vite (web) | Similar JavaScript/Vite workflow, but the project has no Vue code; requires learning Vue and replacing existing React UI. | Mature web choices exist (for example, Chart.js/ECharts and browser QR scanning with ZXing); no package was evaluated for production use. | Web build is platform-independent; no macOS needed. | Shares browser standards and API contracts, not React components. | Can be built in a Node/Vite container just like React; it does not improve the existing service boundary. |
| Flutter (native) | Dart and Flutter are new to this repository; additional framework learning is required. | Native QR and chart packages are available (for example, `mobile_scanner`, `qr_flutter`, and `fl_chart`); compatibility was not tested here. | iOS builds require macOS and Xcode; Android can be built with the Android toolchain. | Flutter UI is separate from the React web UI; API models/business rules may be shared only if deliberately extracted. | Native app builds need their own Flutter/Android build environment; not part of the current web Docker service. |
| React Native (native) | JavaScript knowledge transfers, but React Native is not React DOM and needs native-module/build knowledge. | Native camera/QR and chart packages are available; package compatibility and maintenance were not tested here. | iOS builds require macOS and Xcode; Android needs its SDK/Gradle toolchain. | Can share some JavaScript validation/API code, but not the web component tree. | Mobile builds remain separate from the web Docker service and need native SDKs. |
| Swift (iOS native) | Requires Swift/iOS skills not evidenced in this repository. | Native scanning/chart frameworks or packages are available; not evaluated because iOS is out of scope. | Requires macOS and Xcode. | Separate app and platform-specific code. | Not a fit for the current Android-only target or Docker web service. |
| Kotlin (Android native) | Already recorded as the team's Android direction in the Charter/SRS; actual team Android experience is not evidenced by a repository scaffold. | Android QR/scanning and chart libraries are available; no library was installed or validated for this project. | Android builds use JDK, Gradle and Android SDK; no macOS requirement. | Separate UI from React web; share API contract and potentially plain business rules. | Android APK builds need a separate native build environment; do not put them in the web Docker image. |

### Prototype evidence

- **React + Vite:** Ran `npm run build` successfully and all 9 frontend tests
  passed. Started the existing app and called
  `/api/v1/occupancy/current` through Vite's proxy; both page and API returned
  HTTP 200. The real API currently returns `current_count: null`, which is an
  empty-data state, not a valid count.
- **Vue + Vite:** Scaffolded a temporary, uncommitted Vue app, built it
  successfully, and rendered an empty/loading/error-aware screen after calling
  the same real endpoint through a Vite proxy; page and API returned HTTP 200.
  The spike added no Vue dependencies to the repository.
- **Native:** No blank-app/API prototype was run. This machine has no Android
  SDK, `adb`, Gradle, or Flutter installation, and the repository has no native
  app scaffold. Therefore the native recommendation below is not backed by a
  runtime/build spike.
- **QR/chart packages:** No candidate package was added or tested for either
  web framework or native platform. Select and verify concrete libraries when
  the corresponding UI stories are implemented.

### Recommendation and alternatives

- **Web:** Retain React + Vite. It is already integrated, builds in the current
  Docker setup, passes its tests, and successfully calls the live backend. Vue
  also passed a minimal API spike, but switching would replace working React
  code without a demonstrated benefit.
- **Native:** Retain Android native with Kotlin, consistent with the recorded
  project scope and Android-only target. Do not select Flutter or React Native
  solely for hypothetical code sharing: both still require a distinct mobile
  UI/build pipeline, while iOS is out of scope. Swift is not selected because
  it targets iOS.
- **Approval / follow-up:** Uyên approved React + Vite and Android native with
  Kotlin on 2026-11-10. Before native implementation is considered validated,
  run a 30-minute Kotlin blank-app/API spike on a machine with Android SDK and
  Gradle; Uyên will assign the runner and record the result in SEAT-48. Do not
  claim the native build or QR/chart integrations have been tested.
- **Dependencies:** This decision record is for SEAT-48 and the SRS topics
  Q-16/Q-17. SEAT-31 remains an upstream dependency for the dependent
  implementation work.