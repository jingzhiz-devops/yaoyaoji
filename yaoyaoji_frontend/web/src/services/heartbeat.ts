/**
 * WebSocket 心跳服务
 *
 * 负责建立 WebSocket 连接、定期发送心跳、断线自动重连。
 */
export class HeartbeatService {
  private ws: WebSocket | null = null
  private heartbeatTimer: number | null = null
  private reconnectTimer: number | null = null
  private reconnectAttempts = 0
  private currentToken: string | null = null

  constructor(
    private readonly heartbeatInterval = 30000,    // 30 秒
    private readonly maxReconnectAttempts = 5,
    private readonly reconnectDelay = 3000          // 初始 3 秒
  ) {}

  /** 建立 WebSocket 连接 */
  connect(token: string): void {
    // 先断开已有连接
    this.disconnect()
    this.currentToken = token

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsBase = import.meta.env.VITE_WS_BASE_URL || `${wsProtocol}//${window.location.host}`
    const url = `${wsBase}/api/ws/heartbeat?token=${encodeURIComponent(token)}`

    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      this.reconnectAttempts = 0
      this.startHeartbeat()
    }

    this.ws.onclose = (event: CloseEvent) => {
      this.stopHeartbeat()
      // Token 无效或用户不存在，不重连
      if (event.code === 4001 || event.code === 4002) {
        this.currentToken = null
        return
      }
      this.attemptReconnect()
    }

    this.ws.onerror = () => {
      // onclose 会随后触发，在那里处理重连
    }
  }

  /** 断开连接并清理所有资源 */
  disconnect(): void {
    this.stopHeartbeat()
    this.stopReconnect()
    if (this.ws) {
      this.ws.onclose = null
      this.ws.onerror = null
      this.ws.onopen = null
      if (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING) {
        this.ws.close(1000)
      }
      this.ws = null
    }
    this.currentToken = null
    this.reconnectAttempts = 0
  }

  private startHeartbeat(): void {
    this.heartbeatTimer = window.setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }))
      }
    }, this.heartbeatInterval)
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer !== null) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  private stopReconnect(): void {
    if (this.reconnectTimer !== null) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts || !this.currentToken) return

    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts)
    this.reconnectAttempts++

    this.reconnectTimer = window.setTimeout(() => {
      if (this.currentToken) {
        this.connect(this.currentToken)
      }
    }, delay)
  }
}

export const heartbeatService = new HeartbeatService()
