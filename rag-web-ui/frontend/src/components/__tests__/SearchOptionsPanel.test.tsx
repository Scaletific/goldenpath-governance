import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import SearchOptionsPanel from '../SearchOptionsPanel'
import { DEFAULT_SEARCH_OPTIONS } from '@/lib/types'

function renderPanel(overrides: Partial<Parameters<typeof SearchOptionsPanel>[0]> = {}) {
  const onChange = vi.fn()
  const props = {
    options: DEFAULT_SEARCH_OPTIONS,
    onChange,
    memoryAvailable: false,
    ...overrides,
  }
  const result = render(<SearchOptionsPanel {...props} />)
  return { ...result, onChange }
}

describe('SearchOptionsPanel', () => {
  it('renders the toggle button', () => {
    renderPanel()
    expect(screen.getByText('Search Options')).toBeInTheDocument()
  })

  it('expands panel when toggle is clicked', async () => {
    const user = userEvent.setup()
    renderPanel()

    await user.click(screen.getByText('Search Options'))

    expect(screen.getByText('Graph Expansion')).toBeVisible()
    expect(screen.getByText('BM25 Keyword Search')).toBeVisible()
    expect(screen.getByText('Query Rewriting')).toBeVisible()
    expect(screen.getByText('Stream Responses')).toBeVisible()
    expect(screen.getByText('Agent Memory')).toBeVisible()
    expect(screen.getByText('Graph Depth')).toBeVisible()
    expect(screen.getByText('Point in Time')).toBeVisible()
  })

  it('calls onChange when Graph Expansion is toggled off', async () => {
    const user = userEvent.setup()
    const { onChange } = renderPanel()

    await user.click(screen.getByText('Search Options'))
    await user.click(screen.getByRole('checkbox', { name: /graph expansion/i }))

    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({ expandGraph: false })
    )
  })

  it('calls onChange when BM25 is toggled off', async () => {
    const user = userEvent.setup()
    const { onChange } = renderPanel()

    await user.click(screen.getByText('Search Options'))
    await user.click(screen.getByRole('checkbox', { name: /bm25 keyword search/i }))

    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({ useBm25: false })
    )
  })

  it('disables Agent Memory checkbox when memoryAvailable is false', async () => {
    const user = userEvent.setup()
    renderPanel({ memoryAvailable: false })

    await user.click(screen.getByText('Search Options'))

    const memoryCheckbox = screen.getByRole('checkbox', { name: /agent memory/i })
    expect(memoryCheckbox).toBeDisabled()
  })

  it('enables Agent Memory checkbox when memoryAvailable is true', async () => {
    const user = userEvent.setup()
    renderPanel({ memoryAvailable: true })

    await user.click(screen.getByText('Search Options'))

    const memoryCheckbox = screen.getByRole('checkbox', { name: /agent memory/i })
    expect(memoryCheckbox).toBeEnabled()
  })

  it('shows offline indicator when memory is unavailable', async () => {
    const user = userEvent.setup()
    renderPanel({ memoryAvailable: false })

    await user.click(screen.getByText('Search Options'))

    expect(screen.getByText('(offline)')).toBeInTheDocument()
  })

  it('clamps Graph Depth to 1-3 range', async () => {
    const user = userEvent.setup()
    const { onChange } = renderPanel()

    await user.click(screen.getByText('Search Options'))

    const depthInput = screen.getByRole('spinbutton')
    await user.clear(depthInput)
    await user.type(depthInput, '5')

    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({ expandDepth: 3 })
    )
  })

  it('shows clear button when Point in Time is set', async () => {
    const user = userEvent.setup()
    const { onChange } = renderPanel({
      options: { ...DEFAULT_SEARCH_OPTIONS, pointInTime: '2026-01-01T00:00' },
    })

    await user.click(screen.getByText('Search Options'))

    const clearBtn = screen.getByText('clear')
    expect(clearBtn).toBeInTheDocument()

    await user.click(clearBtn)
    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({ pointInTime: '' })
    )
  })
})
