import { useState } from 'react'
import { ChevronDown, ExternalLink, FileText } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { EvidenceItem } from '@/lib/types'

interface EvidenceCardProps {
  evidence: EvidenceItem
  index: number
  onViewDocument?: (path: string) => void
}

export default function EvidenceCard({ evidence, index, onViewDocument }: EvidenceCardProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="rounded-lg border border-gray-200 bg-white text-sm">
      {/* Collapsed summary — always visible, click to toggle */}
      <button
        type="button"
        onClick={() => setExpanded((e) => !e)}
        aria-expanded={expanded}
        className="flex w-full items-center gap-2 p-3 text-left hover:bg-gray-50 transition-colors duration-150 rounded-lg"
      >
        <ChevronDown
          className={cn(
            'h-3.5 w-3.5 shrink-0 text-gray-400 transition-transform duration-200',
            !expanded && '-rotate-90'
          )}
        />
        <span className="font-medium text-gray-700">Source {index + 1}</span>

        {/* Inline graph_id badges */}
        {evidence.graph_ids.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {evidence.graph_ids.map((id) => (
              <span
                key={id}
                className="rounded bg-blue-50 px-1.5 py-0.5 font-mono text-xs text-blue-700"
              >
                {id}
              </span>
            ))}
          </div>
        )}
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
            {/* File paths — clickable to open full doc */}
            {evidence.file_paths.length > 0 && (
              <div className="flex items-start gap-1.5 text-gray-600">
                <FileText className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                <div className="space-y-0.5">
                  {evidence.file_paths.map((fp) => (
                    <button
                      key={fp}
                      type="button"
                      onClick={() => onViewDocument?.(fp)}
                      className="flex items-center gap-1 font-mono text-xs break-all text-blue-600 hover:text-blue-800 hover:underline text-left"
                    >
                      {fp}
                      <ExternalLink className="h-2.5 w-2.5 shrink-0" />
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Excerpt */}
            {evidence.excerpt && (
              <div className="mt-2 border-l-2 border-gray-200 pl-2 text-xs text-gray-500 italic">
                {evidence.excerpt}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
