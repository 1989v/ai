import type { ArtifactEntry } from '../types'

const ARTIFACT_URL = /^https:\/\/claude\.ai\/(?:code\/)?artifact\/[A-Za-z0-9_-]+/
const URL_IN_TEXT = /"url"\s*:\s*"(https:\/\/claude\.ai\/(?:code\/)?artifact\/[A-Za-z0-9_-]+[^"]*)"/

export const MAX_ENTRIES = 200

type Published = { url: string; title: string }

function asRecord(value: unknown): Record<string, unknown> | undefined {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : undefined
}

/** action 이 없거나 publish 인 호출만 발행이다. asset 업로드는 페이지를 바꾸지 않으니 뺀다. */
export function isPublishCall(input: unknown): boolean {
  const args = asRecord(input)
  if (args === undefined) return false
  const action = args.action
  return (action === undefined || action === 'publish') && args.asset !== true
}

function basename(path: unknown): string | undefined {
  if (typeof path !== 'string' || path === '') return undefined
  return path.split('/').filter(Boolean).at(-1)
}

/**
 * 발행 결과에서 URL 과 제목을 꺼낸다. 결과 레코드가 없으면(헤드리스 기록 등)
 * 모델이 읽은 텍스트에서 "url" 필드를 찾는다.
 */
export function publishedFrom(input: unknown, result: unknown, text?: string): Published | undefined {
  const args = asRecord(input) ?? {}
  let record = asRecord(result)
  if (record === undefined && typeof text === 'string') {
    try {
      record = asRecord(JSON.parse(text))
    } catch {
      const found = URL_IN_TEXT.exec(text)
      if (found?.[1]) record = { url: found[1] }
    }
  }
  if (record === undefined || record.opened === true) return undefined

  const url = record.url
  if (typeof url !== 'string' || !ARTIFACT_URL.test(url)) return undefined

  const title =
    [record.title, args.title, basename(args.file_path)].find(
      (one): one is string => typeof one === 'string' && one.trim() !== '',
    ) ?? url
  return { url, title: title.trim() }
}

/** 같은 URL 은 한 줄로 합치고 맨 뒤(가장 최근)로 옮긴다. */
export function mergePublish(entries: readonly ArtifactEntry[], item: Published, at: number | undefined): ArtifactEntry[] {
  const prior = entries.find(one => one.url === item.url)
  const rest = entries.filter(one => one.url !== item.url)
  const merged: ArtifactEntry = {
    url: item.url,
    title: item.title,
    publishes: (prior?.publishes ?? 0) + 1,
    ...(at === undefined ? (prior?.updatedAt === undefined ? {} : { updatedAt: prior.updatedAt }) : { updatedAt: at }),
  }
  return [...rest, merged].slice(-MAX_ENTRIES)
}

type ToolUseLike = { tool: string; input: Record<string, unknown>; result?: unknown; text?: string; isError?: true }

/** 대화 기록의 Artifact 발행 호출을 순서대로 다시 모은다. 시각은 기록에 없어 비워 둔다. */
export function scanToolUses(uses: readonly ToolUseLike[]): ArtifactEntry[] {
  let entries: ArtifactEntry[] = []
  for (const use of uses) {
    if (use.tool !== 'Artifact' || use.isError === true || !isPublishCall(use.input)) continue
    const item = publishedFrom(use.input, use.result, use.text)
    if (item !== undefined) entries = mergePublish(entries, item, undefined)
  }
  return entries
}

/**
 * 저장본을 기준으로 기록에서만 보이는 항목을 앞쪽(더 오래된 쪽)에 더한다.
 * 저장본이 없으면 기록 순서를 그대로 쓴다.
 */
export function combine(stored: readonly ArtifactEntry[], scanned: readonly ArtifactEntry[]): ArtifactEntry[] {
  const known = new Set(stored.map(one => one.url))
  return [...scanned.filter(one => !known.has(one.url)), ...stored].slice(-MAX_ENTRIES)
}

function isWide(code: number): boolean {
  return (
    (code >= 0x1100 && code <= 0x115f) ||
    (code >= 0x2e80 && code <= 0xa4cf) ||
    (code >= 0xac00 && code <= 0xd7a3) ||
    (code >= 0xf900 && code <= 0xfaff) ||
    (code >= 0xfe30 && code <= 0xfe4f) ||
    (code >= 0xff00 && code <= 0xff60) ||
    (code >= 0xffe0 && code <= 0xffe6) ||
    (code >= 0x1f300 && code <= 0x1faff) ||
    code >= 0x20000
  )
}

/** 터미널 칸 수 기준으로 자른다. 한글·CJK·이모지는 두 칸. */
export function fitCells(text: string, cells: number): string {
  if (cells <= 0) return ''
  const chars = Array.from(text)
  const width = (ch: string) => (isWide(ch.codePointAt(0) ?? 0) ? 2 : 1)
  if (chars.reduce((sum, ch) => sum + width(ch), 0) <= cells) return text

  let used = 0
  let out = ''
  for (const ch of chars) {
    if (used + width(ch) > cells - 1) break
    out += ch
    used += width(ch)
  }
  return `${out}…`
}

export function ago(now: number, at: number | undefined): string {
  if (at === undefined) return '시각 모름'
  const minutes = Math.floor(Math.max(0, now - at) / 60_000)
  if (minutes < 1) return '방금'
  if (minutes < 60) return `${minutes}분 전`
  const hours = Math.floor(minutes / 60)
  return `${hours}시간 ${minutes % 60}분 전`
}

/**
 * 세션 기록 파일(jsonl)에서 뽑을 두 조각. 기록은 JSON 이라 본문 속 따옴표는 \" 로 적혀,
 * 이 패턴은 실제 도구 호출·결과 레코드에만 걸린다.
 */
export const TRANSCRIPT_PATTERNS = [
  '"type":"tool_use","id":"[^"]+","name":"Artifact","input":\\{[^}]*\\}',
  '"tool_use_id":"[^"]+","type":"tool_result","content":(\\[\\{"type":"text","text":)?"Published [^"]* at https://claude\\.ai/(code/)?artifact/[A-Za-z0-9_-]+',
] as const

const USE_PIECE = /^"type":"tool_use","id":"([^"]+)","name":"Artifact","input":(\{[^}]*\})$/
const RESULT_PIECE = /^"tool_use_id":"([^"]+)".*?"Published [^"]* at (https:\/\/claude\.ai\/(?:code\/)?artifact\/[A-Za-z0-9_-]+)$/

function inputOf(raw: string): Record<string, unknown> {
  try {
    return asRecord(JSON.parse(raw)) ?? {}
  } catch {
    // 중첩 객체가 있는 입력은 잘려 나온다. 판정에 쓰는 필드만 읽는다.
    const field = (name: string) => new RegExp(`"${name}":"([^"]*)"`).exec(raw)?.[1]
    return {
      ...(field('action') ? { action: field('action') } : {}),
      ...(/"asset":true/.test(raw) ? { asset: true } : {}),
      ...(field('title') ? { title: field('title') } : {}),
      ...(field('file_path') ? { file_path: field('file_path') } : {}),
    }
  }
}

/** 발행에 쓴 파일 경로 또는 제목. 제목은 `<title>` 을 읽을 수 있을 때 그것으로 바꾼다. */
export type TranscriptPublish = { url: string; title: string; filePath?: string }

/**
 * `grep -o` 로 뽑은 줄들을 발행 기록으로 바꾼다. 결과가 "Published … at <url>" 인 호출만 발행이다.
 * 컴팩션으로 대화에서 사라진 앞부분과 플러그인 설치 전 발행도 여기서 나온다.
 */
export function scanTranscript(pieces: string): TranscriptPublish[] {
  const inputs = new Map<string, Record<string, unknown>>()
  const out: TranscriptPublish[] = []
  for (const line of pieces.split('\n')) {
    const use = USE_PIECE.exec(line)
    if (use) {
      inputs.set(use[1], inputOf(use[2]))
      continue
    }
    const result = RESULT_PIECE.exec(line)
    if (!result) continue
    const input = inputs.get(result[1])
    if (input === undefined || !isPublishCall(input)) continue
    const filePath = typeof input.file_path === 'string' ? input.file_path : undefined
    const title = [input.title, basename(filePath)].find(
      (one): one is string => typeof one === 'string' && one.trim() !== '',
    )
    out.push({ url: result[2], title: (title ?? result[2]).trim(), ...(filePath ? { filePath } : {}) })
  }
  return out
}

/** 발행한 HTML 의 `<title>`. 아티팩트 제목이 이것이라 파일 이름보다 낫다. */
export function htmlTitle(html: string): string | undefined {
  const found = /<title[^>]*>([^<]*)<\/title>/i.exec(html.slice(0, 8192))?.[1]?.trim()
  return found ? found.replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>') : undefined
}

/** 기록에서 모은 발행을 순서대로 합친다(같은 URL 은 한 줄, 발행 횟수 누적). */
export function entriesFrom(publishes: readonly TranscriptPublish[]): ArtifactEntry[] {
  let entries: ArtifactEntry[] = []
  for (const one of publishes) entries = mergePublish(entries, one, undefined)
  return entries
}
