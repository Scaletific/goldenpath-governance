import { useState, useRef, useEffect } from 'react'
import { Send } from 'lucide-react'
import type { SearchOptions } from '@/lib/types'
import SearchOptionsPanel from '@/components/SearchOptionsPanel'

interface ChatInputProps {
  onSend: (question: string) => void
  disabled: boolean
  searchOptions: SearchOptions
  onSearchOptionsChange: (options: SearchOptions) => void
  memoryAvailable: boolean
}

export default function ChatInput({
  onSend,
  disabled,
  searchOptions,
  onSearchOptionsChange,
  memoryAvailable,
}: ChatInputProps) {
  const [input, setInput] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [input])

  const handleSubmit = () => {
    const trimmed = input.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setInput('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div>
      <div className="flex items-end gap-2 rounded-2xl border border-gray-300 bg-white px-4 py-3 shadow-sm focus-within:border-blue-400 focus-within:ring-1 focus-within:ring-blue-400">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a governance question..."
          disabled={disabled}
          rows={1}
          className="max-h-32 flex-1 resize-none bg-transparent text-sm outline-none placeholder:text-gray-400 disabled:opacity-50"
        />
        <button
          onClick={handleSubmit}
          disabled={disabled || !input.trim()}
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-600 text-white transition-colors hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          <Send className="h-4 w-4" />
        </button>
      </div>
      <SearchOptionsPanel
        options={searchOptions}
        onChange={onSearchOptionsChange}
        memoryAvailable={memoryAvailable}
      />
    </div>
  )
}
