import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { AlertTriangle, ArrowRight, ChevronDown, Clock, User, Bot } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { Message } from '@/lib/types'
import EvidenceCard from './EvidenceCard'
import SourceList from './SourceList'

interface MessageBubbleProps {
  message: Message
  onViewDocument?: (path: string) => void
}

export default function MessageBubble({ message, onViewDocument }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const contract = message.contract
  const isUnknown = contract?.answer === 'unknown'

  const [evidenceOpen, setEvidenceOpen] = useState(false)
  const [sourcesOpen, setSourcesOpen] = useState(false)

  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-blue-600">
          <Bot className="h-4 w-4" />
        </div>
      )}

      <div
        className={`max-w-2xl rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-blue-600 text-white'
            : isUnknown
              ? 'bg-amber-50 border border-amber-200'
              : 'bg-white border border-gray-200'
        }`}
      >
        {/* Answer text */}
        <div className={`prose prose-sm max-w-none ${isUser ? 'prose-invert' : ''}`}>
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        {/* Contract fields (assistant only) */}
        {contract && !isUser && (
          <div className="mt-3 space-y-3">
            {/* Evidence — collapsible section */}
            {contract.evidence.length > 0 && (
              <div>
                <button
                  type="button"
                  onClick={() => setEvidenceOpen((o) => !o)}
                  aria-expanded={evidenceOpen}
                  className="mb-1.5 flex w-full items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-gray-400 hover:text-gray-600 transition-colors duration-150"
                >
                  <ChevronDown
                    className={cn(
                      'h-3.5 w-3.5 transition-transform duration-200',
                      !evidenceOpen && '-rotate-90'
                    )}
                  />
                  Sources
                  <span className="rounded-full bg-gray-100 px-1.5 py-0.5 text-[10px] font-medium text-gray-500 normal-case">
                    {contract.evidence.length}
                  </span>
                </button>
                <div
                  className={cn(
                    'grid transition-all duration-200',
                    evidenceOpen ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
                  )}
                >
                  <div className="overflow-hidden">
                    <div className="space-y-2">
                      {contract.evidence.map((ev, i) => (
                        <EvidenceCard key={i} evidence={ev} index={i} onViewDocument={onViewDocument} />
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Retrieval Sources — collapsible section */}
            {contract.sources && contract.sources.length > 0 && (
              <div>
                <button
                  type="button"
                  onClick={() => setSourcesOpen((o) => !o)}
                  aria-expanded={sourcesOpen}
                  className="mb-1.5 flex w-full items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-gray-400 hover:text-gray-600 transition-colors duration-150"
                >
                  <ChevronDown
                    className={cn(
                      'h-3.5 w-3.5 transition-transform duration-200',
                      !sourcesOpen && '-rotate-90'
                    )}
                  />
                  Retrieval Sources
                  <span className="rounded-full bg-gray-100 px-1.5 py-0.5 text-[10px] font-medium text-gray-500 normal-case">
                    {contract.sources.length}
                  </span>
                </button>
                <div
                  className={cn(
                    'grid transition-all duration-200',
                    sourcesOpen ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
                  )}
                >
                  <div className="overflow-hidden">
                    <SourceList sources={contract.sources} onViewDocument={onViewDocument} />
                  </div>
                </div>
              </div>
            )}

            {/* Limitations */}
            {contract.limitations && (
              <div className="flex items-start gap-1.5 rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-700">
                <AlertTriangle className="mt-0.5 h-3 w-3 shrink-0" />
                <span>{contract.limitations}</span>
              </div>
            )}

            {/* Next step */}
            {contract.next_step && (
              <div className="flex items-start gap-1.5 rounded-md bg-blue-50 px-3 py-2 text-xs text-blue-700">
                <ArrowRight className="mt-0.5 h-3 w-3 shrink-0" />
                <span>{contract.next_step}</span>
              </div>
            )}

            {/* Provider, elapsed & timestamp */}
            <div className="flex items-center gap-2 text-[10px] text-gray-400">
              {message.provider && <span>{message.provider}</span>}
              {contract.elapsed_ms != null && (
                <span className="flex items-center gap-0.5">
                  <Clock className="h-2.5 w-2.5" />
                  {contract.elapsed_ms < 1000
                    ? `${contract.elapsed_ms}ms`
                    : `${(contract.elapsed_ms / 1000).toFixed(1)}s`}
                </span>
              )}
              <span>{new Date(contract.timestamp).toLocaleTimeString()}</span>
            </div>
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-200 text-gray-600">
          <User className="h-4 w-4" />
        </div>
      )}
    </div>
  )
}
