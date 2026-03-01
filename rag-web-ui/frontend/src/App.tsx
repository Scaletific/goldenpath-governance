import { useState, useEffect, useRef, useCallback } from 'react'
import { Loader2 } from 'lucide-react'
import type { Message, ProviderInfo, SearchOptions } from '@/lib/types'
import { DEFAULT_SEARCH_OPTIONS } from '@/lib/types'
import { askQuestion, askQuestionStream, getProviders, healthCheck } from '@/lib/api'
import MessageBubble from '@/components/MessageBubble'
import ChatInput from '@/components/ChatInput'
import DocumentViewer from '@/components/DocumentViewer'
import ProviderSelect from '@/components/ProviderSelect'

export default function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [providers, setProviders] = useState<ProviderInfo[]>([])
  const [selectedProvider, setSelectedProvider] = useState('ollama')
  const [loading, setLoading] = useState(false)
  const [loadingPhase, setLoadingPhase] = useState('')
  const [viewDocPath, setViewDocPath] = useState<string | null>(null)
  const [searchOptions, setSearchOptions] = useState<SearchOptions>(DEFAULT_SEARCH_OPTIONS)
  const [memoryAvailable, setMemoryAvailable] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const streamContentRef = useRef('')
  const streamRafRef = useRef<number>()

  const handleViewDocument = useCallback((path: string) => {
    setViewDocPath(path)
  }, [])

  useEffect(() => {
    getProviders()
      .then(setProviders)
      .catch(() => {
        setProviders([
          { id: 'ollama', name: 'Ollama (Local)', available: true },
          { id: 'claude', name: 'Claude', available: true },
          { id: 'openai', name: 'OpenAI', available: true },
          { id: 'gemini', name: 'Gemini', available: true },
        ])
      })

    healthCheck()
      .then((h) => {
        setMemoryAvailable(!!(h as Record<string, unknown>).graphiti)
      })
      .catch(() => setMemoryAvailable(false))
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async (question: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: question,
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMessage])
    setLoading(true)
    setLoadingPhase('')

    const requestPayload = {
      question,
      provider: selectedProvider,
      expand_graph: searchOptions.expandGraph,
      use_bm25: searchOptions.useBm25,
      point_in_time: searchOptions.pointInTime || undefined,
      expand_depth: searchOptions.expandDepth,
      expand_query_synonyms: searchOptions.expandQuerySynonyms,
      enable_memory: searchOptions.enableMemory,
    }

    try {
      if (searchOptions.stream) {
        const assistantId = crypto.randomUUID()
        streamContentRef.current = ''
        setMessages((prev) => [...prev, {
          id: assistantId,
          role: 'assistant',
          content: '',
          timestamp: new Date().toISOString(),
          provider: selectedProvider,
        }])

        const contract = await askQuestionStream(
          requestPayload,
          (token) => {
            streamContentRef.current += token
            // Throttle React renders to animation frame rate (~60fps)
            // to avoid React 18 batching swallowing intermediate updates
            if (!streamRafRef.current) {
              streamRafRef.current = requestAnimationFrame(() => {
                const content = streamContentRef.current
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantId
                      ? { ...m, content }
                      : m
                  )
                )
                streamRafRef.current = undefined
              })
            }
          },
          (status) => {
            setLoadingPhase(
              status.phase === 'retrieving'
                ? 'Retrieving...'
                : `Synthesizing (${status.sources_count ?? 0} sources)...`
            )
          },
          (error) => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, content: `Error: ${error}` }
                  : m
              )
            )
          },
        )

        // Flush any pending animation frame
        if (streamRafRef.current) {
          cancelAnimationFrame(streamRafRef.current)
          streamRafRef.current = undefined
        }

        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? { ...m, contract, timestamp: contract.timestamp }
              : m
          )
        )
      } else {
        const contract = await askQuestion(requestPayload)

        const assistantMessage: Message = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: contract.answer,
          contract,
          timestamp: contract.timestamp,
          provider: selectedProvider,
        }

        setMessages((prev) => [...prev, assistantMessage])
      }
    } catch (err) {
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `Failed to get answer: ${err instanceof Error ? err.message : 'Unknown error'}`,
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
      setLoadingPhase('')
    }
  }

  return (
    <div className="flex h-screen flex-col bg-gray-50">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-gray-200 bg-white px-6 py-3">
        <div>
          <h1 className="text-lg font-semibold text-gray-900">
            GoldenPath RAG
          </h1>
          <p className="text-xs text-gray-500">
            Governance knowledge base — contract-driven answers
          </p>
        </div>
        <div className="flex items-center gap-3">
          {providers.length > 0 && (
            <ProviderSelect
              providers={providers}
              selected={selectedProvider}
              onChange={setSelectedProvider}
            />
          )}
        </div>
      </header>

      {/* Messages */}
      <main className="flex-1 overflow-y-auto px-6 py-4">
        {messages.length === 0 ? (
          <div className="flex h-full items-center justify-center">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-gray-400">
                Ask a governance question
              </h2>
              <p className="mt-1 text-sm text-gray-400">
                Query governance documents — ADRs, policies, runbooks, PRDs
              </p>
            </div>
          </div>
        ) : (
          <div className="mx-auto max-w-3xl space-y-4">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} onViewDocument={handleViewDocument} />
            ))}
            {loading && (
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <Loader2 className="h-4 w-4 animate-spin" />
                {loadingPhase || 'Retrieving and synthesizing...'}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      {/* Input */}
      <footer className="border-t border-gray-200 bg-white px-6 py-4">
        <div className="mx-auto max-w-3xl">
          <ChatInput
            onSend={handleSend}
            disabled={loading}
            searchOptions={searchOptions}
            onSearchOptionsChange={setSearchOptions}
            memoryAvailable={memoryAvailable}
          />
        </div>
      </footer>

      {/* Document viewer side panel */}
      <DocumentViewer path={viewDocPath} onClose={() => setViewDocPath(null)} />
    </div>
  )
}
