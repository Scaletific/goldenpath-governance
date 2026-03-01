import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { FileText, Loader2, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { fetchDocument } from '@/lib/api'
import type { DocumentResponse } from '@/lib/types'

interface DocumentViewerProps {
  path: string | null
  onClose: () => void
}

export default function DocumentViewer({ path, onClose }: DocumentViewerProps) {
  const [doc, setDoc] = useState<DocumentResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!path) {
      setDoc(null)
      return
    }

    setLoading(true)
    setError(null)

    fetchDocument(path)
      .then(setDoc)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [path])

  const isOpen = path !== null

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/20 transition-opacity duration-200"
          onClick={onClose}
        />
      )}

      {/* Side panel */}
      <div
        className={cn(
          'fixed right-0 top-0 z-50 flex h-full w-full max-w-2xl flex-col bg-white shadow-2xl transition-transform duration-300',
          isOpen ? 'translate-x-0' : 'translate-x-full'
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
          <div className="flex items-center gap-2 min-w-0">
            <FileText className="h-4 w-4 shrink-0 text-gray-500" />
            <span className="truncate font-mono text-sm text-gray-600">
              {path}
            </span>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-1 hover:bg-gray-100 transition-colors"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {/* Title bar */}
        {doc && (
          <div className="border-b border-gray-100 px-6 py-3">
            <h2 className="text-lg font-semibold text-gray-900">{doc.title}</h2>
            <div className="mt-1 flex items-center gap-2">
              {doc.doc_id && (
                <span className="rounded bg-blue-50 px-2 py-0.5 font-mono text-xs text-blue-700">
                  {doc.doc_id}
                </span>
              )}
              {doc.doc_type && (
                <span className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-500">
                  {doc.doc_type}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {loading && (
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading document...
            </div>
          )}

          {error && (
            <div className="rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          {doc && !loading && (
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown>{doc.content}</ReactMarkdown>
            </div>
          )}
        </div>
      </div>
    </>
  )
}
