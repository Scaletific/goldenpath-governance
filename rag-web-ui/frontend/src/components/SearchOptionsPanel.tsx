import { useEffect, useState } from 'react'
import { ChevronDown, Info, Settings2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { SearchOptions } from '@/lib/types'

const OPTION_DESCRIPTIONS = {
  expandGraph: 'Traverses Neo4j relationships to find related documents beyond direct keyword matches',
  useBm25: 'Adds traditional keyword matching alongside vector similarity for better recall',
  expandQuerySynonyms: 'Uses the LLM to rephrase your question with synonyms and related terms before searching',
  stream: 'Shows the answer word-by-word as the LLM generates it instead of waiting for the full response',
  enableMemory: 'Searches previous Q&A episodes stored in Graphiti to add conversational context',
  expandDepth: 'How many relationship hops to traverse in Neo4j (1 = direct links, 2 = links of links, 3 = three hops)',
  pointInTime: 'Filter results to documents that existed before this date — useful for historical governance questions',
}

function InfoTooltip({ text }: { text: string }) {
  return (
    <span className="relative group ml-1 inline-flex">
      <Info className="h-3 w-3 text-gray-400 hover:text-gray-600 cursor-help" />
      <span className="invisible group-hover:visible absolute bottom-full left-1/2 -translate-x-1/2 mb-1.5 w-48 rounded bg-gray-800 px-2.5 py-1.5 text-[11px] leading-tight text-white shadow-lg z-10">
        {text}
      </span>
    </span>
  )
}

interface SearchOptionsPanelProps {
  options: SearchOptions
  onChange: (options: SearchOptions) => void
  memoryAvailable: boolean
}

export default function SearchOptionsPanel({
  options,
  onChange,
  memoryAvailable,
}: SearchOptionsPanelProps) {
  const [open, setOpen] = useState(false)
  const [overflowVisible, setOverflowVisible] = useState(false)

  useEffect(() => {
    if (open) {
      const timer = setTimeout(() => setOverflowVisible(true), 200)
      return () => clearTimeout(timer)
    } else {
      setOverflowVisible(false)
    }
  }, [open])

  const update = (patch: Partial<SearchOptions>) => {
    onChange({ ...options, ...patch })
  }

  return (
    <div className="mt-2">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-700 transition-colors"
      >
        <Settings2 className="h-3.5 w-3.5" />
        <span>Search Options</span>
        <ChevronDown
          className={cn(
            'h-3 w-3 transition-transform duration-200',
            !open && '-rotate-90'
          )}
        />
      </button>

      <div
        className="grid transition-[grid-template-rows] duration-200 ease-in-out"
        style={{ gridTemplateRows: open ? '1fr' : '0fr' }}
      >
        <div className={overflowVisible ? '' : 'overflow-hidden'}>
          <div className="grid grid-cols-2 gap-x-6 gap-y-2 pt-3 pb-1">
            {/* Checkboxes column 1 */}
            <label className="flex items-center gap-2 text-xs text-gray-600 cursor-pointer">
              <input
                type="checkbox"
                checked={options.expandGraph}
                onChange={(e) => update({ expandGraph: e.target.checked })}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              Graph Expansion
              <InfoTooltip text={OPTION_DESCRIPTIONS.expandGraph} />
            </label>

            <label className="flex items-center gap-2 text-xs text-gray-600 cursor-pointer">
              <input
                type="checkbox"
                checked={options.useBm25}
                onChange={(e) => update({ useBm25: e.target.checked })}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              BM25 Keyword Search
              <InfoTooltip text={OPTION_DESCRIPTIONS.useBm25} />
            </label>

            <label className="flex items-center gap-2 text-xs text-gray-600 cursor-pointer">
              <input
                type="checkbox"
                checked={options.expandQuerySynonyms}
                onChange={(e) => update({ expandQuerySynonyms: e.target.checked })}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              Query Rewriting
              <InfoTooltip text={OPTION_DESCRIPTIONS.expandQuerySynonyms} />
            </label>

            <label className="flex items-center gap-2 text-xs text-gray-600 cursor-pointer">
              <input
                type="checkbox"
                checked={options.stream}
                onChange={(e) => update({ stream: e.target.checked })}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              Stream Responses
              <InfoTooltip text={OPTION_DESCRIPTIONS.stream} />
            </label>

            <label
              className={cn(
                'flex items-center gap-2 text-xs cursor-pointer',
                memoryAvailable ? 'text-gray-600' : 'text-gray-400'
              )}
            >
              <input
                type="checkbox"
                checked={options.enableMemory}
                disabled={!memoryAvailable}
                onChange={(e) => update({ enableMemory: e.target.checked })}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 disabled:opacity-50"
              />
              Agent Memory
              <InfoTooltip text={OPTION_DESCRIPTIONS.enableMemory} />
              {!memoryAvailable && (
                <span className="text-[10px] text-gray-400">(offline)</span>
              )}
            </label>

            {/* Number / datetime inputs */}
            <label className="flex items-center gap-2 text-xs text-gray-600">
              Graph Depth
              <InfoTooltip text={OPTION_DESCRIPTIONS.expandDepth} />
              <input
                type="number"
                min={1}
                max={3}
                value={options.expandDepth}
                onChange={(e) =>
                  update({ expandDepth: Math.max(1, Math.min(3, Number(e.target.value))) })
                }
                className="w-14 rounded border border-gray-300 px-2 py-0.5 text-xs focus:border-blue-400 focus:ring-1 focus:ring-blue-400"
              />
            </label>

            <label className="col-span-2 flex items-center gap-2 text-xs text-gray-600">
              Point in Time
              <InfoTooltip text={OPTION_DESCRIPTIONS.pointInTime} />
              <input
                type="datetime-local"
                value={options.pointInTime}
                onChange={(e) => update({ pointInTime: e.target.value })}
                className="rounded border border-gray-300 px-2 py-0.5 text-xs focus:border-blue-400 focus:ring-1 focus:ring-blue-400"
              />
              {options.pointInTime && (
                <button
                  type="button"
                  onClick={() => update({ pointInTime: '' })}
                  className="text-gray-400 hover:text-gray-600 text-[10px] underline"
                >
                  clear
                </button>
              )}
            </label>
          </div>
        </div>
      </div>
    </div>
  )
}
