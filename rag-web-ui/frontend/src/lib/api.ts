import type { AnswerContract, AskRequest, DocumentResponse, ProviderInfo } from './types'

const API_BASE = '/api'

export async function askQuestion(request: AskRequest): Promise<AnswerContract> {
  const response = await fetch(`${API_BASE}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Ask failed: ${response.status} ${error}`)
  }

  return response.json()
}

export async function getProviders(): Promise<ProviderInfo[]> {
  const response = await fetch(`${API_BASE}/providers`)

  if (!response.ok) {
    throw new Error(`Failed to fetch providers: ${response.status}`)
  }

  return response.json()
}

export async function fetchDocument(path: string): Promise<DocumentResponse> {
  const response = await fetch(`${API_BASE}/document?path=${encodeURIComponent(path)}`)

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Failed to fetch document: ${response.status} ${error}`)
  }

  return response.json()
}

export async function healthCheck(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE}/health`)

  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`)
  }

  return response.json()
}

export async function askQuestionStream(
  request: AskRequest,
  onToken: (text: string) => void,
  onStatus: (status: { phase: string; sources_count?: number }) => void,
  onError: (error: string) => void,
): Promise<AnswerContract> {
  const response = await fetch(`${API_BASE}/ask/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Stream failed: ${response.status} ${error}`)
  }

  if (!response.body) {
    throw new Error('Streaming response body not available')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let contract: AnswerContract | null = null
  let currentEvent = ''
  let buffer = ''
  const yieldToUi = () => new Promise<void>((resolve) => setTimeout(resolve, 0))

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    // Process all complete lines (SSE events end with \n\n)
    const lines = buffer.split('\n')
    // Keep the last element — it may be an incomplete line
    buffer = lines.pop() ?? ''
    for (const line of lines) {
      if (line.startsWith('event: ')) {
        currentEvent = line.slice(7).trim()
      } else if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6))
          switch (currentEvent) {
            case 'token':
              onToken(data.text)
              // Yield to allow UI paint between token bursts even if buffered in one chunk
              await yieldToUi()
              break
            case 'status': onStatus(data); break
            case 'complete': contract = data as AnswerContract; break
            case 'error': onError(data.message); break
          }
        } catch {
          // Skip malformed JSON lines
        }
      }
    }
  }
  if (!contract) throw new Error('Stream ended without complete event')
  return contract
}
