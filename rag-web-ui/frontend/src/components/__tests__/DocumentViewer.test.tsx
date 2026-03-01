import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import DocumentViewer from '../DocumentViewer'

// Mock the api module
vi.mock('@/lib/api', () => ({
  fetchDocument: vi.fn(),
}))

import { fetchDocument } from '@/lib/api'

const mockFetch = vi.mocked(fetchDocument)

describe('DocumentViewer', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('does not render content when path is null', () => {
    const { container } = render(<DocumentViewer path={null} onClose={vi.fn()} />)
    // Panel should have translate-x-full (off-screen)
    const panel = container.querySelector('.translate-x-full')
    expect(panel).toBeInTheDocument()
  })

  it('shows loading state while fetching', () => {
    // Never resolve the promise to keep loading state
    mockFetch.mockReturnValue(new Promise(() => {}))

    render(<DocumentViewer path="docs/test.md" onClose={vi.fn()} />)

    expect(screen.getByText('Loading document...')).toBeInTheDocument()
  })

  it('shows document content after successful fetch', async () => {
    mockFetch.mockResolvedValue({
      file_path: 'docs/test.md',
      title: 'Test Document',
      content: '# Hello World',
      doc_id: 'DOC-001',
      doc_type: 'policy',
    })

    render(<DocumentViewer path="docs/test.md" onClose={vi.fn()} />)

    await waitFor(() => {
      expect(screen.getByText('Test Document')).toBeInTheDocument()
    })

    expect(screen.getByText('DOC-001')).toBeInTheDocument()
    expect(screen.getByText('policy')).toBeInTheDocument()
    expect(screen.getByText('Hello World')).toBeInTheDocument()
  })

  it('shows error state on fetch failure', async () => {
    mockFetch.mockRejectedValue(new Error('Not found'))

    render(<DocumentViewer path="docs/missing.md" onClose={vi.fn()} />)

    await waitFor(() => {
      expect(screen.getByText('Not found')).toBeInTheDocument()
    })
  })

  it('calls onClose when close button is clicked', async () => {
    const user = userEvent.setup()
    mockFetch.mockResolvedValue({
      file_path: 'docs/test.md',
      title: 'Test',
      content: 'body',
    })
    const onClose = vi.fn()

    render(<DocumentViewer path="docs/test.md" onClose={onClose} />)

    // Find the close button (the one with the X icon)
    const buttons = screen.getAllByRole('button')
    const closeButton = buttons.find((b) => b.querySelector('svg'))
    expect(closeButton).toBeDefined()
    await user.click(closeButton!)

    expect(onClose).toHaveBeenCalledOnce()
  })

  it('calls onClose when backdrop is clicked', async () => {
    const user = userEvent.setup()
    mockFetch.mockResolvedValue({
      file_path: 'docs/test.md',
      title: 'Test',
      content: 'body',
    })
    const onClose = vi.fn()

    const { container } = render(<DocumentViewer path="docs/test.md" onClose={onClose} />)

    // Backdrop is the fixed div with bg-black/20
    const backdrop = container.querySelector('.bg-black\\/20')
    expect(backdrop).toBeInTheDocument()
    await user.click(backdrop!)

    expect(onClose).toHaveBeenCalledOnce()
  })

  it('displays file path in header', () => {
    mockFetch.mockReturnValue(new Promise(() => {}))

    render(<DocumentViewer path="docs/adrs/ADR-042.md" onClose={vi.fn()} />)

    expect(screen.getByText('docs/adrs/ADR-042.md')).toBeInTheDocument()
  })
})
