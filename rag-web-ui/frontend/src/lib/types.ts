/**
 * Mirrors the AnswerContract from schemas/metadata/answer_contract.schema.json.
 * The backend returns this shape; the frontend renders all fields.
 */

export interface EvidenceItem {
  graph_ids: string[]
  file_paths: string[]
  excerpt?: string
  source_sha?: string
}

export interface SourceItem {
  doc_id: string
  section: string
  file_path: string
  score: number
  source: string
  excerpt: string
  related_docs: string[]
}

export interface AnswerContract {
  answer: string
  evidence: EvidenceItem[]
  timestamp: string
  limitations: string
  next_step: string
  elapsed_ms?: number
  sources?: SourceItem[]
}

export interface SearchOptions {
  expandGraph: boolean
  useBm25: boolean
  pointInTime: string
  expandDepth: number
  expandQuerySynonyms: boolean
  enableMemory: boolean
  stream: boolean
}

export const DEFAULT_SEARCH_OPTIONS: SearchOptions = {
  expandGraph: true,
  useBm25: true,
  pointInTime: '',
  expandDepth: 1,
  expandQuerySynonyms: true,
  enableMemory: false,
  stream: true,
}

export interface AskRequest {
  question: string
  provider?: string
  top_k?: number
  expand_graph?: boolean
  use_bm25?: boolean
  point_in_time?: string
  expand_depth?: number
  expand_query_synonyms?: boolean
  enable_memory?: boolean
}

export interface ProviderInfo {
  id: string
  name: string
  available: boolean
}

export interface DocumentResponse {
  file_path: string
  title: string
  content: string
  doc_id?: string
  doc_type?: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  contract?: AnswerContract
  timestamp: string
  provider?: string
}
