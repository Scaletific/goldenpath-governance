import type { ProviderInfo } from '@/lib/types'

interface ProviderSelectProps {
  providers: ProviderInfo[]
  selected: string
  onChange: (provider: string) => void
}

export default function ProviderSelect({ providers, selected, onChange }: ProviderSelectProps) {
  return (
    <select
      value={selected}
      onChange={(e) => onChange(e.target.value)}
      className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-400"
    >
      {providers.map((p) => (
        <option key={p.id} value={p.id} disabled={!p.available}>
          {p.name} {!p.available && '(unavailable)'}
        </option>
      ))}
    </select>
  )
}
