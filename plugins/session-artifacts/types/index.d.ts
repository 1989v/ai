export type ArtifactEntry = {
  url: string
  title: string
  /** `$.clock.now()` 기준 마지막 발행 시각. 대화 기록에서 복구한 항목은 시각을 모른다. */
  updatedAt?: number
  publishes: number
}

export type SessionArtifacts = {
  /** 이 목록이 속한 세션. 현재 세션 id 와 다르면 다시 복구한다. */
  sessionId: string | null
  entries: ArtifactEntry[]
}

declare module 'claude-code' {
  interface PluginState {
    'session-artifacts': { current: SessionArtifacts }
  }
}
