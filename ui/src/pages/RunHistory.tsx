import { useEffect, useState } from 'react'
import { useRunStore } from '../stores/runStore'
import { api } from '../api'

interface RunDetail {
  id: number
  type: string
  protocol_key: string
  question: string
  status: string
  cost_usd: number
  started_at: string | null
  completed_at: string | null
  outputs: { agent_key: string; output_text: string; model: string }[]
}

export default function RunHistory() {
  const { runs, fetch: fetchRuns } = useRunStore()
  const [selected, setSelected] = useState<RunDetail | null>(null)

  useEffect(() => { fetchRuns() }, [fetchRuns])

  const loadDetail = async (id: number) => {
    try {
      const detail = await api.runs.get(id) as unknown as RunDetail
      setSelected(detail)
    } catch { /* ignore */ }
  }

  return (
    <div className="max-w-5xl">
      <p className="text-xs font-bold tracking-wider uppercase text-text-muted mb-4">History</p>

      {runs.length === 0 ? (
        <p className="text-sm text-text-muted">No runs yet. Go to the Run page to execute a protocol.</p>
      ) : (
        <div className="bg-card border border-border rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left px-4 py-2 text-xs font-bold tracking-wider uppercase text-text-muted">ID</th>
                <th className="text-left px-4 py-2 text-xs font-bold tracking-wider uppercase text-text-muted">Type</th>
                <th className="text-left px-4 py-2 text-xs font-bold tracking-wider uppercase text-text-muted">Protocol</th>
                <th className="text-left px-4 py-2 text-xs font-bold tracking-wider uppercase text-text-muted">Question</th>
                <th className="text-left px-4 py-2 text-xs font-bold tracking-wider uppercase text-text-muted">Status</th>
                <th className="text-right px-4 py-2 text-xs font-bold tracking-wider uppercase text-text-muted">Cost</th>
              </tr>
            </thead>
            <tbody>
              {runs.map(run => (
                <tr
                  key={run.id}
                  onClick={() => loadDetail(run.id)}
                  className="border-b border-border last:border-0 hover:bg-elevated/50 cursor-pointer transition"
                >
                  <td className="px-4 py-2 text-text-muted">#{run.id}</td>
                  <td className="px-4 py-2 text-text">{run.type}</td>
                  <td className="px-4 py-2 text-text">{run.protocol_key || '—'}</td>
                  <td className="px-4 py-2 text-text truncate max-w-xs">{run.question}</td>
                  <td className="px-4 py-2">
                    <StatusBadge status={run.status} />
                  </td>
                  <td className="px-4 py-2 text-right text-text-muted">${run.cost_usd.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Detail panel */}
      {selected && (
        <div className="mt-6 bg-card border border-border rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-text">Run #{selected.id} — {selected.protocol_key}</h3>
            <button onClick={() => setSelected(null)} className="text-text-muted hover:text-text text-xs">Close</button>
          </div>
          <p className="text-sm text-text-muted mb-4">{selected.question}</p>

          {selected.outputs?.map((out, i) => (
            <div key={i} className="mb-3 bg-white border border-border rounded-lg p-3">
              <span className="text-xs font-medium text-text-muted">{out.agent_key}</span>
              <div className="text-sm text-text whitespace-pre-wrap font-mono mt-1 max-h-64 overflow-y-auto">
                {out.output_text}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    pending: 'bg-gray-100 text-gray-600 border-gray-200',
    running: 'bg-blue-50 text-blue-600 border-blue-200',
    completed: 'bg-green-50 text-green-600 border-green-200',
    failed: 'bg-red-50 text-red-600 border-red-200',
  }
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium border ${styles[status] || styles.pending}`}>
      {status}
    </span>
  )
}
