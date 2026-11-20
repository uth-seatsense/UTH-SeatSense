/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_OCCUPANCY_API_URL?: string;
  readonly VITE_USE_MOCK?: string;
  readonly VITE_MOCK_OCCUPANCY_STATE?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
