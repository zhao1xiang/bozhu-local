/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string
  readonly VITE_SKIP_SPLASH?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// 声明 Tauri 全局对象
interface Window {
  __TAURI__?: any
}
