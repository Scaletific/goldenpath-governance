import { describe, it, expect, vi, beforeEach } from 'vitest'
import { askQuestionStream } from '../api'

function createSSEStream(events: Array<{ event: string; data: string }>) {
  const text = events
    .map((e) => `event: ${e.event}\ndata: ${e.data}\n\n`)
    .join('')
  const encoder = new TextEncoder()
  const stream = new ReadableStream({
    start(controller) {
      controller.enqueue(encoder.encode(text))
      controller.close()
    },
  })
  return stream
}

describe('askQuestionStream', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('parses token events and calls onToken', async () => {
    const tokens: string[] = []
    const contract = {
      answer: 'Hello world.',
      evidence: [],
      sources: [],
      timestamp: '2026-02-10T12:00:00Z',
      limitations: 'Test.',
      next_step: '',
    }

    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        body: createSSEStream([
          { event: 'status', data: JSON.stringify({ phase: 'retrieving' }) },
          { event: 'status', data: JSON.stringify({ phase: 'synthesizing', sources_count: 3 }) },
          { event: 'token', data: JSON.stringify({ text: 'Hello ' }) },
          { event: 'token', data: JSON.stringify({ text: 'world.' }) },
          { event: 'complete', data: JSON.stringify(contract) },
        ]),
      })
    )

    const result = await askQuestionStream(
      { question: 'test' },
      (text) => tokens.push(text),
      () => {},
      () => {}
    )

    expect(tokens).toEqual(['Hello ', 'world.'])
    expect(result.answer).toBe('Hello world.')
    expect(result.evidence).toEqual([])
  })

  it('calls onStatus for status events', async () => {
    const statuses: Array<{ phase: string }> = []
    const contract = {
      answer: 'Test.',
      evidence: [],
      sources: [],
      timestamp: '2026-02-10T12:00:00Z',
      limitations: '',
      next_step: '',
    }

    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        body: createSSEStream([
          { event: 'status', data: JSON.stringify({ phase: 'retrieving' }) },
          { event: 'status', data: JSON.stringify({ phase: 'synthesizing', sources_count: 5 }) },
          { event: 'token', data: JSON.stringify({ text: 'Test.' }) },
          { event: 'complete', data: JSON.stringify(contract) },
        ]),
      })
    )

    await askQuestionStream(
      { question: 'test' },
      () => {},
      (status) => statuses.push(status),
      () => {}
    )

    expect(statuses).toHaveLength(2)
    expect(statuses[0]).toEqual({ phase: 'retrieving' })
    expect(statuses[1]).toEqual({ phase: 'synthesizing', sources_count: 5 })
  })

  it('calls onError for error events', async () => {
    const errors: string[] = []
    const contract = {
      answer: '',
      evidence: [],
      sources: [],
      timestamp: '2026-02-10T12:00:00Z',
      limitations: '',
      next_step: '',
    }

    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        body: createSSEStream([
          { event: 'status', data: JSON.stringify({ phase: 'retrieving' }) },
          { event: 'error', data: JSON.stringify({ message: 'LLM timeout' }) },
          { event: 'complete', data: JSON.stringify(contract) },
        ]),
      })
    )

    await askQuestionStream(
      { question: 'test' },
      () => {},
      () => {},
      (error) => errors.push(error)
    )

    expect(errors).toEqual(['LLM timeout'])
  })

  it('throws when stream ends without complete event', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        body: createSSEStream([
          { event: 'status', data: JSON.stringify({ phase: 'retrieving' }) },
          { event: 'token', data: JSON.stringify({ text: 'partial' }) },
        ]),
      })
    )

    await expect(
      askQuestionStream(
        { question: 'test' },
        () => {},
        () => {},
        () => {}
      )
    ).rejects.toThrow('Stream ended without complete event')
  })

  it('throws when response is not ok', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        text: vi.fn().mockResolvedValue('Internal Server Error'),
      })
    )

    await expect(
      askQuestionStream(
        { question: 'test' },
        () => {},
        () => {},
        () => {}
      )
    ).rejects.toThrow('Stream failed: 500')
  })
})
