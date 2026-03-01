import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ChatInput from '../ChatInput'
import type { SearchOptions } from '@/lib/types'
import { DEFAULT_SEARCH_OPTIONS } from '@/lib/types'

function renderInput(overrides: Partial<Parameters<typeof ChatInput>[0]> = {}) {
  const defaults = {
    onSend: vi.fn(),
    disabled: false,
    searchOptions: { ...DEFAULT_SEARCH_OPTIONS } as SearchOptions,
    onSearchOptionsChange: vi.fn(),
    memoryAvailable: true,
  }
  const props = { ...defaults, ...overrides }
  const result = render(<ChatInput {...props} />)
  return { ...result, props }
}

/** The send button is the rounded-full button (SearchOptionsPanel toggle is not). */
function getSendButton() {
  return screen
    .getAllByRole('button')
    .find((b) => b.classList.contains('rounded-full'))!
}

describe('ChatInput', () => {
  it('renders textarea and send button', () => {
    renderInput()
    expect(screen.getByPlaceholderText('Ask a governance question...')).toBeInTheDocument()
    expect(getSendButton()).toBeInTheDocument()
  })

  it('send button is disabled when input is empty', () => {
    renderInput()
    expect(getSendButton()).toBeDisabled()
  })

  it('send button is disabled when disabled prop is true', () => {
    renderInput({ disabled: true })
    const textarea = screen.getByPlaceholderText('Ask a governance question...')
    expect(textarea).toBeDisabled()
    expect(getSendButton()).toBeDisabled()
  })

  it('Enter sends message and clears input', async () => {
    const user = userEvent.setup()
    const { props } = renderInput()
    const textarea = screen.getByPlaceholderText('Ask a governance question...')

    await user.type(textarea, 'What is GOV-0017?')
    await user.keyboard('{Enter}')

    expect(props.onSend).toHaveBeenCalledWith('What is GOV-0017?')
    expect(textarea).toHaveValue('')
  })

  it('Shift+Enter does not send message', async () => {
    const user = userEvent.setup()
    const { props } = renderInput()
    const textarea = screen.getByPlaceholderText('Ask a governance question...')

    await user.type(textarea, 'line one')
    await user.keyboard('{Shift>}{Enter}{/Shift}')
    await user.type(textarea, 'line two')

    expect(props.onSend).not.toHaveBeenCalled()
  })

  it('click send button sends message', async () => {
    const user = userEvent.setup()
    const { props } = renderInput()
    const textarea = screen.getByPlaceholderText('Ask a governance question...')

    await user.type(textarea, 'Hello')
    await user.click(getSendButton())

    expect(props.onSend).toHaveBeenCalledWith('Hello')
  })

  it('does not send whitespace-only input', async () => {
    const user = userEvent.setup()
    renderInput()
    const textarea = screen.getByPlaceholderText('Ask a governance question...')

    await user.type(textarea, '   ')
    expect(getSendButton()).toBeDisabled()
  })
})
