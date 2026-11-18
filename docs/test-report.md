# Test report

## Validation run — 2026-11-15

Scope: documentation updates; frontend source was not changed. Commands ran
from `frontend` after restoring dependencies with `npm.cmd ci`.

| Command | Result | Notes |
|---|---|---|
| `npm.cmd run format:check` | Failed | Prettier reports formatting issues in 14 existing frontend source/test files. They were not changed as part of the original documentation task. |
| `npm.cmd test` | Passed | 4 test files, 39 tests. |
| `npm.cmd run lint` | Passed with warnings | Exit code 0; 0 errors and 14 existing `react/prop-types` warnings in `src/pages/DashboardPage.jsx`. |
| `npm.cmd run build` | Passed | Vite production build completed. |

Backend, Docker Compose, end-to-end, and native Android tests were not run
during that initial documentation validation. Later results are recorded below.
This report records command outcomes only; it is not evidence that Sprint 4
requirements or external Jira acceptance criteria have been completed.

## Validation run — 2026-11-15 (Backend, Docker, Android)

| Command / check | Result | Notes |
|---|---|---|
| `$env:SEAT24_RUN_DB_TESTS = '1'; .\.venv\Scripts\python.exe -m pytest backend\tests -q` | Failed: 25 passed, 1 failed | `test_cv_batch_receipt_and_idempotent_retry`: retrying the same CV batch returns HTTP 409 instead of the expected HTTP 200. This run enables the real PostgreSQL persistence tests. |
| `$env:SEAT24_RUN_DB_TESTS = '1'; .\.venv\Scripts\python.exe -m unittest discover -s database\tests -p test_cv_migration.py -v` | Passed: 6 tests | PostgreSQL migration/constraint tests ran in a disposable container. |
| `$env:SEAT24_RUN_COMPOSE_TESTS = '1'; .\.venv\Scripts\python.exe -m unittest discover -s database\tests -p test_compose_persistence.py -v` | Passed: 2 tests | Isolated Compose checks covered fresh database bootstrap, migration upgrade, Backend write/read, database outage, restart, and persistence. Temporary test resources were cleaned up. |
| `docker compose config --quiet` | Passed | Compose configuration parsed successfully. |
| `http://localhost:8000/health/db` and `http://localhost:3000/` | Passed: HTTP 200 each | Smoke checks against the already-running local Backend and Frontend containers. |
| Android project/toolchain check | Blocked | No Android project, Gradle wrapper, `AndroidManifest.xml`, `adb`, or Android SDK environment variables were present. No APK/runtime test could be performed. |

At the time of this initial run, the Backend retry failure was unresolved and
the Android module/toolchain was not present. Follow-up fixes and validation
are recorded below; neither run alone constitutes full Sprint 4 acceptance.

## Validation run — 2026-11-15 (mobile implementation follow-up)

| Command / check | Result | Notes |
|---|---|---|
| `$env:SEAT24_RUN_DB_TESTS = '1'; .\.venv\Scripts\python.exe -m pytest backend\tests -q` | Passed: 31 tests | Includes CV idempotent retry and new OTP/session, room, booking, and single-use QR API tests. One Starlette/httpx deprecation warning remains. SMTP delivery is mocked in API tests. |
| `$env:SEAT24_RUN_COMPOSE_TESTS = '1'; .\.venv\Scripts\python.exe -m unittest discover -s database\tests -p test_compose_persistence.py -v` | Passed: 2 tests | Disposable Compose projects; fresh bootstrap verifies migration 009 and safe reapplication, and persistence coverage includes backend health/restart. No user database volume was modified. |
| `docker compose config --quiet` | Passed | Compose accepts the new OTP, SMTP, and booking environment variables. |
| `gradle -p android testDebugUnitTest assembleDebug --no-daemon` using Gradle 8.11.1 and Android SDK 35 | Passed | Kotlin compilation and debug APK packaging succeeded. `testDebugUnitTest` reported `NO-SOURCE`; no Android unit tests exist yet. APK: `android/app/build/outputs/apk/debug/app-debug.apk`. |
| `.\android\gradlew.bat testDebugUnitTest assembleDebug` | Blocked on first attempt | Gradle Wrapper distribution download ended with a connection reset. The wrapper was generated; the same build succeeded using the locally downloaded Gradle distribution. |
| `adb devices` | No devices attached | APK was not installed/launched; Android runtime and camera/QR scanning remain unverified. |
| Frontend tests/build | Not rerun in this follow-up | No frontend source changed. The previous run remains 39/39 tests and build passed; `format:check` still reports the 14 pre-existing files listed above. |
| `git diff --check` | Passed | No whitespace errors in the worktree. |

The UTC/naive datetime comparison causing the earlier CV retry 409 was fixed;
the latest full Backend suite now passes. API 26 remains a provisional minimum
pending product confirmation. SMTP delivery against an actual mail server,
Android runtime/E2E, and applying migration 009 to an existing user volume
were not tested; existing PostgreSQL volumes require a backup and manual
migration as described in `database/README.md`.

## Validation run — 2026-11-16 (web API integration)

| Command / check | Result | Notes |
|---|---|---|
| `npm.cmd test` | Passed: 37 tests | Covers OTP requests, shared Bearer token use across web API endpoints, backend error handling, protected routes, and the Android-compatible QR payload. |
| `npm.cmd run lint` | Passed with warnings | Exit code 0; 0 errors and 16 `react/prop-types` warnings (14 existing in Dashboard components and 2 for auth component children). |
| `npm.cmd run build` | Passed | Vite production build completed with locally generated QR rendering. |
| Prettier on changed frontend files | Passed | Changed JS/JSX/CSS files were formatted. The repository-wide check now reports 6 unrelated existing files: `main.jsx`, `HealthPage.jsx`, `HomePage.jsx`, `App.test.jsx`, `DashboardStatus.test.jsx`, and `Health.test.js`. |

The web now calls the same Backend auth, rooms, occupancy, booking and check-in
routes as Android. No browser-to-live-Backend OTP/booking/QR camera E2E was run;
it requires a configured SMTP server and a ready database. Camera scanning uses
the browser `BarcodeDetector` API when supported, with QR text input as fallback.
