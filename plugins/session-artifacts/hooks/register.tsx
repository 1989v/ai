import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { ArtifactEntry, SessionArtifacts } from '../types'
import {
  ago,
  chunk,
  combine,
  entriesFrom,
  fitCells,
  GAP,
  htmlTitle,
  isPublishCall,
  layout,
  mergePublish,
  publishedFrom,
  scanToolUses,
  scanTranscript,
  toggleLabel,
  TRANSCRIPT_PATTERNS,
} from './artifacts'

const STORE_KEY = 'sessions'
const KEPT_SESSIONS = 30
const TOGGLE = 'toggle'

const EMPTY: SessionArtifacts = { sessionId: null, entries: [] }
const current = atom({ plugin: 'session-artifacts', key: 'current' } as const, EMPTY)
const expanded = atom({ plugin: 'session-artifacts', key: 'expanded' } as const, false)

type Saved = Record<string, { savedAt: number; entries: ArtifactEntry[] }>

async function loadSaved($: EngineInterface): Promise<Saved> {
  const value = await $.store.get(STORE_KEY)
  return typeof value === 'object' && value !== null ? (value as Saved) : {}
}

/** /resume 로 돌아왔을 때 쓰려고 세션 id 별로 남긴다. 오래된 세션부터 지운다. */
async function save($: EngineInterface, state: SessionArtifacts): Promise<void> {
  if (state.sessionId === null) return
  const saved = await loadSaved($)
  saved[state.sessionId] = { savedAt: await $.clock.now(), entries: state.entries }
  const kept = Object.entries(saved)
    .sort(([, a], [, b]) => b.savedAt - a.savedAt)
    .slice(0, KEPT_SESSIONS)
  await $.store.set(STORE_KEY, Object.fromEntries(kept))
}

/**
 * 상태가 지금 세션 것인지 확인하고, 아니면 저장본 + 대화 기록으로 다시 채운다.
 * 대화 기록은 컴팩션 뒤 앞부분이 요약으로 바뀌므로 저장본이 우선이다.
 */
async function ensureCurrent($: EngineInterface): Promise<void> {
  const sessionId = await $.session.id()
  const state = await read($, current)
  if (state.sessionId === sessionId) return

  const stored = (await loadSaved($))[sessionId]?.entries ?? []
  const messages = await $.session.messages()
  const scanned = scanToolUses(messages.flatMap(message => message.toolUses))
  const history = await transcriptEntries($, sessionId)
  const next: SessionArtifacts = { sessionId, entries: combine(stored, combine(scanned, history)) }
  await update($, current, () => next)
}

/**
 * 세션 기록 파일 전체에서 발행을 다시 모은다. 대화(`$.session.messages`)에는 컴팩션 뒤 부분만 남고,
 * 플러그인을 켜기 전 발행은 저장본에도 없다. 기록 파일은 수십 MB 라 grep 으로 필요한 조각만 읽는다.
 * 기록 형식은 공개 계약이 아니어서, 무엇이 실패하든 빈 목록으로 두고 다른 경로를 막지 않는다.
 */
async function transcriptEntries($: EngineInterface, sessionId: string): Promise<ArtifactEntry[]> {
  if (!/^[A-Za-z0-9-]+$/.test(sessionId)) return []
  try {
    const configDir = (await $.env.get('CLAUDE_CONFIG_DIR')) ?? `${await $.env.get('HOME')}/.claude`
    const found = await $.process.run(['find', `${configDir}/projects`, '-maxdepth', '2', '-name', `${sessionId}.jsonl`])
    const path = found.stdout.split('\n').find(line => line.trim() !== '')
    if (path === undefined) return []
    const grep = await $.process.run(['grep', '-oE', '-e', TRANSCRIPT_PATTERNS[0], '-e', TRANSCRIPT_PATTERNS[1], path])
    const publishes = scanTranscript(grep.stdout)
    const titles = new Map<string, string>()
    for (const filePath of new Set(publishes.flatMap(one => (one.filePath ? [one.filePath] : [])))) {
      try {
        const html = await $.fs.read(filePath)
        const title = typeof html === 'string' ? htmlTitle(html) : undefined
        if (title) titles.set(filePath, title)
      } catch {
        // 지운 파일은 파일 이름을 제목으로 둔다.
      }
    }
    return entriesFrom(publishes.map(one => ({ ...one, title: (one.filePath && titles.get(one.filePath)) || one.title })))
  } catch {
    return []
  }
}

function listText(entries: readonly ArtifactEntry[], now: number): string {
  if (entries.length === 0) return '이 세션에서 발행한 아티팩트가 없습니다.'
  const lines = [...entries].reverse().map((one, i) => {
    const times = one.publishes > 1 ? ` · 발행 ${one.publishes}회` : ''
    return `${i + 1}. ${one.title} (갱신 ${ago(now, one.updatedAt)}${times})\n   ${one.url}`
  })
  return [`이 세션 아티팩트 ${entries.length}건`, ...lines].join('\n')
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'session-artifacts',
      description: '이 세션에서 발행한 아티팩트 링크 전체 목록',
    })
    await ensureCurrent($)
    return next(e)
  })

  // 복구가 실패해도 프롬프트를 막지 않는다.
  on('prompt.submit', async ($, e, next) => {
    await ensureCurrent($)
    return next(e)
  }).catch(($, e, next) => next(e))

  on('session.end', async ($, e, next) => {
    if (e.reason === 'clear' || e.reason === 'resume') {
      await update($, current, () => EMPTY)
      await update($, expanded, () => false)
    }
    return next(e)
  })

  // 기록이 실패해도 도구 결과는 그대로 둔다. next 는 이미 난 결과를 다시 돌려줄 뿐 도구를 두 번 돌리지 않는다.
  on('tool.call', { tool: 'Artifact' }, async ($, e, next) => {
    const ran = await next(e)
    if (ran.deny !== undefined || ran.isError === true || !isPublishCall(e)) return ran

    const item = publishedFrom(e, ran.result, ran.text)
    if (item === undefined) return ran

    await ensureCurrent($)
    const now = await $.clock.now()
    const state = await update($, current, state => ({
      ...state,
      entries: mergePublish(state.entries, item, now),
    }))
    await save($, state)
    return ran
  }).catch(($, e, next) => next(e))

  on('command.run', { command: 'session-artifacts' }, async $ => {
    await ensureCurrent($)
    const { entries } = await read($, current)
    return { text: listText(entries, await $.clock.now()) }
  })

  // 첫 줄에 최근 것부터 나란히. 다 못 보이면 줄 끝 버튼이 전체를 펼치고 다시 접는다.
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) return next(e)
    const { entries } = await read($, current)
    if (entries.length === 0) return next(e)

    const { Box, Text, Link, Button } = $.ui.resolve(e)
    const { perRow, itemCells, hidden } = layout(Math.max(8, e.props.bodyColumns), entries.length)
    const isOpen = hidden > 0 && (await read($, expanded))
    const newest = [...entries].reverse()
    const rows = chunk(isOpen ? newest : newest.slice(0, perRow), perRow)

    return (
      <Box flexDirection="column">
        {rows.map((row, i) => (
          <Box key={`row-${i}`} gap={GAP}>
            {row.map(one => (
              <Box key={one.url} width={itemCells}>
                <Text color="suggestion">↗ </Text>
                <Link href={one.url} label={fitCells(one.title, itemCells - 2)} />
              </Box>
            ))}
            {i === 0 && hidden > 0 ? (
              <Button
                key={TOGGLE}
                label={isOpen ? '접기' : toggleLabel(hidden)}
                dimColor
                onPress={() => update($, expanded, open => !open)}
              />
            ) : null}
          </Box>
        ))}
      </Box>
    )
  })
}
