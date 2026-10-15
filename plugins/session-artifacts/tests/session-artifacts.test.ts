import { expect, mock, test } from 'claude-code/testing'
import type { Engine } from 'claude-code/testing'
import type { On, RenderElement, SessionMessage } from 'claude-code'

import { fitCells } from '../hooks/artifacts'

const PLUGIN = 'session-artifacts'
const A = 'https://claude.ai/code/artifact/aaaa1111'
const B = 'https://claude.ai/artifact/bbbb2222'
const C = 'https://claude.ai/code/artifact/cccc3333'
const D = 'https://claude.ai/code/artifact/dddd4444'

type World = { sessionId: string; messages: SessionMessage[] }

/** 엔진 밑바닥: 세션 id·대화 기록·명령 등록·Artifact 도구 결과를 테스트가 정한다. */
function world(on: On, w: World) {
  mock.store(on)
  const clock = mock.clock(on, { now: 1_000_000 })
  on('session.start', ($, e) => ({ cwd: e.cwd }))
  on('session.end', ($, e) => ({ sessionId: e.sessionId }))
  on('prompt.submit', ($, e) => ({ text: e.text }))
  on('session.id', () => ({ value: w.sessionId }))
  // 플러그인이 그리지 않으면 엔진 몫: 빈 상자로 대신한다.
  on('ui.render', { component: 'AbovePrompt' }, ($, e) => {
    const { Box } = $.ui.resolve(e)
    return h(Box, { key: 'engine' }) as RenderElement
  })
  on('session.messages', () => ({ value: w.messages }))
  on('command.register', ($, e) => ({ value: { command: e.name } }))
  on('tool.call', { tool: 'Artifact' }, ($, e) => {
    const args = e as unknown as Record<string, unknown>
    const action = args.action ?? 'publish'
    if (action === 'list') return { result: { artifacts: [{ title: 'x', url: D }] } }
    if (action === 'open') return { result: { opened: true, url: D, artifact_id: 'dddd4444' } }
    if (action === 'pin' || action === 'delete') return { result: { url: D, pinned: true } }
    return { result: { url: String(args.url ?? args.file_path), path: 'index.html', title: args.title } }
  })
  return clock
}

async function publish($: Engine, url: string, title?: string) {
  await $.tool.call({ tool: 'Artifact', action: 'publish', url, file_path: url, ...(title ? { title } : {}) } as never)
}

/** 전체 목록 명령의 출력: 플러그인 상태를 사용자가 보는 그대로 읽는다. */
async function listed($: Engine) {
  const out = await $.command.run({ command: 'session-artifacts' } as never)
  return out.text ?? ''
}

const BAND_PROPS = {
  hasSurvey: false,
  isWorking: false,
  maxRows: 10,
  bodyColumns: 40,
  scroll: { offset: 0, bodyRows: 9, contentRows: 0 },
  view: {},
} as never

test('발행만 모으고 같은 URL 은 한 줄로 합친다', async ($, on) => {
  const clock = world(on, { sessionId: 'S1', messages: [] })
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

  await publish($, A, '보고서')
  await $.tool.call({ tool: 'Artifact', action: 'list' } as never)
  await $.tool.call({ tool: 'Artifact', action: 'open', url: D } as never)
  await $.tool.call({ tool: 'Artifact', action: 'pin', url: D } as never)
  await $.tool.call({ tool: 'Artifact', action: 'delete', url: D } as never)
  await clock.advance(5 * 60_000)
  await publish($, A, '보고서 v2')

  await clock.advance(2 * 60_000)
  const text = await listed($)
  expect(text).toContain('이 세션 아티팩트 1건')
  expect(text).toContain('1. 보고서 v2 (갱신 2분 전 · 발행 2회)')
  expect(text).not.toContain(D)
})

test('0건이면 밴드를 그리지 않고, 4건이면 최근 3건 + 외 1건', async ($, on) => {
  world(on, { sessionId: 'S1', messages: [] })
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

  for (const surface of ['terminal', 'desktop'] as const) {
    const empty = await $.ui.mount({ plugin: PLUGIN, surface, component: 'AbovePrompt', props: BAND_PROPS })
    expect(await empty.find({ key: 'engine' })).toBeDefined()
    expect(await empty.find({ text: /아티팩트/ })).toBeUndefined()
    await empty.unmount()
  }

  await publish($, A, '첫째')
  await publish($, B, '둘째')
  await publish($, C, '셋째')
  await publish($, D, '아주 긴 제목이 붙은 넷째 아티팩트 페이지라서 잘려야 한다')

  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ plugin: PLUGIN, surface, component: 'AbovePrompt', props: BAND_PROPS })
    const links = await ui.findAll({ type: 'Link' })
    expect(links.map(one => one.props.href)).toEqual([D, C, B])
    expect(String(links[0]?.props.label).endsWith('…')).toBe(true)
    expect(await ui.find({ type: 'Text', text: /외 1건/ })).toBeDefined()
    await ui.unmount()
  }
})

test('세션이 바뀌면 대화 기록의 발행 호출로 복구하고 list·open·오류는 뺀다', async ($, on) => {
  const w: World = { sessionId: 'S1', messages: [] }
  world(on, w)
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await publish($, A, '이전 세션')

  w.sessionId = 'S2'
  w.messages = [
    {
      role: 'assistant',
      text: '',
      toolUses: [
        { tool_use_id: '1', tool: 'Artifact', input: { file_path: '/tmp/plan.html' }, result: { url: B, path: 'index.html' } },
        { tool_use_id: '2', tool: 'Artifact', input: { action: 'list' }, result: { artifacts: [{ url: C, title: 'c' }] } },
        { tool_use_id: '3', tool: 'Artifact', input: { action: 'open', url: C }, result: { opened: true, url: C } },
        { tool_use_id: '4', tool: 'Artifact', input: { file_path: '/tmp/x.html' }, text: 'refused', isError: true },
        { tool_use_id: '5', tool: 'Artifact', input: { title: 'Text only' }, text: `{"url":"${D}","path":"index.html"}` },
      ],
    },
  ]
  await $.prompt.submit({ text: 'hi' } as never)

  const text = await listed($)
  expect(text).toContain('이 세션 아티팩트 2건')
  expect(text).toContain(`1. Text only (갱신 시각 모름)\n   ${D}`)
  expect(text).toContain(`2. plan.html (갱신 시각 모름)\n   ${B}`)
  expect(text).not.toContain(A)
  expect(text).not.toContain(C)
})

test('같은 세션으로 돌아오면 기록에 없어도 저장본으로 복구한다', async ($, on) => {
  const w: World = { sessionId: 'S1', messages: [] }
  world(on, w)
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await publish($, A, '보존')

  await $.session.end({ reason: 'resume', sessionId: 'S1', resume: { id: 'S1' } } as never)
  await $.prompt.submit({ text: 'back' } as never)
  const text = await listed($)
  expect(text).toContain(`1. 보존 (갱신 방금)\n   ${A}`)
})

test('/session-artifacts 가 전체 목록을 낸다', async ($, on) => {
  world(on, { sessionId: 'S1', messages: [] })
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await publish($, A, '하나')
  await publish($, B, '둘')

  const text = await listed($)
  expect(text).toContain(`1. 둘 (갱신 방금)\n   ${B}`)
  expect(text).toContain(`2. 하나 (갱신 방금)\n   ${A}`)
})

test('칸 수로 자르고 한글은 두 칸으로 센다', () => {
  expect(fitCells('abc', 3)).toBe('abc')
  expect(fitCells('abcd', 3)).toBe('ab…')
  expect(fitCells('가나다', 5)).toBe('가나…')
  expect(fitCells('가나', 4)).toBe('가나')
})
