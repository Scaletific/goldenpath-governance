import { useState } from 'react'
import { ChevronDown, Database, ExternalLink, FileText, Hash } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { SourceItem } from '@/lib/types'

interface SourceListProps {
  sources: SourceItem[]
  onViewDocument?: (path: string) => void
}

function SourceCard({ src, onViewDocument }: { src: SourceItem; onViewDocument?: (path: string) => void }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="rounded-lg border border-gray-200 bg-gray-50 text-sm">
      {/* Collapsed summary — always visible */}
      <button
        type="button"
        onClick={() => setExpanded((e) => !e)}
        aria-expanded={expanded}
        className="flex w-full items-center gap-2 p-3 text-left hover:bg-gray-100 transition-colors duration-150 rounded-lg"
      >
        <ChevronDown
          className={cn(
            'h-3.5 w-3.5 shrink-0 text-gray-400 transition-transform duration-200',
            !expanded && '-rotate-90'
          )}
        />

        {/* doc_id + section */}
        <div className="flex items-center gap-1.5 min-w-0">
          <Hash className="h-3.5 w-3.5 shrink-0 text-gray-500" />
          <span className="font-medium text-gray-700 truncate">{src.doc_id}</span>
          {src.section && (
            <span className="text-gray-400 truncate">/ {src.section}</span>
          )}
        </div>

        {/* Score + method tag — pushed right */}
        <div className="ml-auto flex items-center gap-2 shrink-0">
          <span className="rounded bg-purple-50 px-1.5 py-0.5 font-mono text-xs text-purple-700">
            {src.source}
          </span>
          <span className="font-mono text-xs text-gray-400">
            {src.score.toFixed(3)}
          </span>
        </div>
      </button>

      {/* Expanded detail — animated */}
      <div
        className={cn(
          'grid transition-all duration-200',
          expanded ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
        )}
      >
        <div className="overflow-hidden">
          <div className="px-3 pb-3 pt-0 space-y-1">
            {/* File path — clickable to open full doc */}
            {src.file_path && (
              <div className="flex items-start gap-1.5 text-gray-600">
                <FileText className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                <button
                  type="button"
                  onClick={() => onViewDocument?.(src.file_path)}
                  className="flex items-center gap-1 font-mono text-xs break-all text-blue-600 hover:text-blue-800 hover:underline text-left"
                >
                  {src.file_path}
                  <ExternalLink className="h-2.5 w-2.5 shrink-0" />
                </button>
              </div>
            )}

            {/* Related docs */}
            {src.related_docs.length > 0 && (
              <div className="flex items-start gap-1.5 text-gray-600">
                <Database className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                <div className="flex flex-wrap gap-1">
                  {src.related_docs.map((rd) => (
                    <span
                      key={rd}
                      className="rounded bg-green-50 px-1.5 py-0.5 font-mono text-xs text-green-700"
                    >
                      {rd}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Excerpt — full text, no line clamp */}
            {src.excerpt && (
              <div className="mt-2 border-l-2 border-gray-200 pl-2 text-xs text-gray-500 italic">
                {src.excerpt}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function SourceList({ sources, onViewDocument }: SourceListProps) {
  if (sources.length === 0) return null

  return (
    <div className="space-y-2">
      {sources.map((src, i) => (
        <SourceCard key={`${src.doc_id}-${i}`} src={src} onViewDocument={onViewDocument} />
      ))}
    </div>
  )
}
