import { useEffect, useState } from 'react'
import { useTeamStore } from '../stores/teamStore'
import { useAgentStore } from '../stores/agentStore'
import { api } from '../api'

export default function Teams() {
  const { teams, currentTeamKeys, currentTeamName, loading, fetch: fetchTeams, removeAgent, setTeamName, clearTeam } = useTeamStore()
  const { agents, fetch: fetchAgents } = useAgentStore()
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => { fetchTeams(); fetchAgents() }, [fetchTeams, fetchAgents])

  const teamAgents = agents.filter((a) => currentTeamKeys.includes(a.key))

  const handleSave = async () => {
    if (currentTeamKeys.length === 0) return
    setSaving(true)
    try {
      await api.teams.create({
        name: currentTeamName,
        agent_keys: currentTeamKeys,
      } as Parameters<typeof api.teams.create>[0])
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
      fetchTeams()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="max-w-4xl">
      <p className="text-xs font-bold tracking-wider uppercase text-text-muted mb-4">Team Composition</p>

      {/* Current team builder */}
      <div className="bg-card border border-border rounded-xl p-6 mb-8">
        <div className="flex items-center justify-between mb-4">
          <input
            type="text"
            value={currentTeamName}
            onChange={(e) => setTeamName(e.target.value)}
            className="text-lg font-semibold text-text bg-transparent border-b border-transparent hover:border-border focus:border-primary focus:outline-none px-1 py-0.5 transition"
          />
          <div className="flex gap-2">
            <button
              onClick={clearTeam}
              className="px-3 py-1.5 rounded-lg text-xs font-medium text-text-muted border border-border hover:bg-elevated transition"
            >
              Clear
            </button>
            <button
              onClick={handleSave}
              disabled={saving || currentTeamKeys.length === 0}
              className="px-4 py-1.5 rounded-lg text-xs font-medium bg-primary text-white hover:bg-primary-hover shadow-sm shadow-primary/20 transition disabled:opacity-50"
            >
              {saving ? 'Saving...' : saved ? 'Saved!' : 'Save Team'}
            </button>
          </div>
        </div>

        {teamAgents.length === 0 ? (
          <p className="text-sm text-text-muted py-8 text-center">
            No agents selected. Go to the Agent Registry to add agents to your team.
          </p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {teamAgents.map((agent, i) => (
              <div key={agent.key} className="bg-white border border-border rounded-lg p-3 flex items-start justify-between">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-text-muted bg-elevated rounded px-1.5 py-0.5">{i + 1}</span>
                    <span className="text-sm font-medium text-text truncate">{agent.name}</span>
                  </div>
                  <span className="text-xs text-text-muted mt-0.5 block">{agent.category}</span>
                </div>
                <button
                  onClick={() => removeAgent(agent.key)}
                  className="shrink-0 text-text-muted hover:text-red-500 transition ml-2"
                  title="Remove"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Saved teams library */}
      <p className="text-xs font-bold tracking-wider uppercase text-text-muted mb-4">Saved Teams</p>
      {loading ? (
        <p className="text-sm text-text-muted">Loading...</p>
      ) : teams.length === 0 ? (
        <p className="text-sm text-text-muted">No saved teams yet.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {teams.map((team) => (
            <div key={team.id} className="bg-card border border-border rounded-xl p-4">
              <h3 className="text-sm font-semibold text-text">{team.name}</h3>
              <p className="text-xs text-text-muted mt-1">
                {team.agent_keys.length} agents
              </p>
              {team.description && (
                <p className="text-xs text-text-muted mt-1">{team.description}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
