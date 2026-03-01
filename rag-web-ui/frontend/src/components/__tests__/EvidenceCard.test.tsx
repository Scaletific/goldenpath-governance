import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import EvidenceCard from '../EvidenceCard'
import type { EvidenceItem } from '@/lib/types'

const baseEvidence: EvidenceItem = {
  graph_ids: ['GOV-0017', 'ADR-042'],
  file_paths: ['docs/governance/policies/GOV-0017-tdd-and-determinism.md'],
  excerpt: 'TDD is mandatory for all platform changes.',
}

describe('EvidenceCard', () => {
  it('renders collapsed by default with source index', () => {
    render(<EvidenceCard evidence={baseEvidence} index={0} />)
    expect(screen.getByText('Source 1')).toBeInTheDocument()
    // Excerpt should not be visible when collapsed (aria-expanded is false)
    expect(screen.getByRole('button', { expanded: false })).toBeInTheDocument()
  })

  it('shows graph_id badges', () => {
    render(<EvidenceCard evidence={baseEvidence} index={0} />)
    expect(screen.getByText('GOV-0017')).toBeInTheDocument()
    expect(screen.getByText('ADR-042')).toBeInTheDocument()
  })

  it('expands on click to show excerpt and file paths', async () => {
    const user = userEvent.setup()
    render(<EvidenceCard evidence={baseEvidence} index={0} />)

    await user.click(screen.getByRole('button', { expanded: false }))

    expect(screen.getByRole('button', { expanded: true })).toBeInTheDocument()
    expect(screen.getByText('TDD is mandatory for all platform changes.')).toBeInTheDocument()
    expect(
      screen.getByText('docs/governance/policies/GOV-0017-tdd-and-determinism.md')
    ).toBeInTheDocument()
  })

  it('collapses on second click', async () => {
    const user = userEvent.setup()
    render(<EvidenceCard evidence={baseEvidence} index={0} />)

    await user.click(screen.getByRole('button', { expanded: false }))
    expect(screen.getByRole('button', { expanded: true })).toBeInTheDocument()

    await user.click(screen.getByRole('button', { expanded: true }))
    expect(screen.getByRole('button', { expanded: false })).toBeInTheDocument()
  })

  it('calls onViewDocument when file path is clicked', async () => {
    const user = userEvent.setup()
    const onView = vi.fn()
    render(<EvidenceCard evidence={baseEvidence} index={0} onViewDocument={onView} />)

    // Expand first
    await user.click(screen.getByRole('button', { expanded: false }))

    // Click the file path button
    const pathButtons = screen.getAllByRole('button')
    const filePathButton = pathButtons.find((b) =>
      b.textContent?.includes('GOV-0017-tdd-and-determinism.md')
    )
    expect(filePathButton).toBeDefined()
    await user.click(filePathButton!)

    expect(onView).toHaveBeenCalledWith(
      'docs/governance/policies/GOV-0017-tdd-and-determinism.md'
    )
  })

  it('renders without excerpt or file paths gracefully', () => {
    const minimal: EvidenceItem = { graph_ids: [], file_paths: [] }
    render(<EvidenceCard evidence={minimal} index={2} />)
    expect(screen.getByText('Source 3')).toBeInTheDocument()
  })
})
