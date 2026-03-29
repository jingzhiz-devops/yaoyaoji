/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_GOOGLE_CLIENT_ID: string
}

interface Window {
  google?: {
    accounts: {
      id: {
        initialize: (config: any) => void
        prompt: (callback?: any) => void
        renderButton: (element: HTMLElement, config: any) => void
      }
    }
  }
}
