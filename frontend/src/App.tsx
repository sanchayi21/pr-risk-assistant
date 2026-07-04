import { useEffect, useState } from "react"

interface PullRequest {
  id: number
  pr_number: number
  title: string
  author: string
  status: string
  created_at: string
}

interface Review {
  summary: string
  risk_score: number
  bugs: string | null
  security_issues: string | null
  test_gaps: string | null
}

interface PRDetail extends PullRequest {
  review: Review | null
}

function RiskBadge({ score }: { score: number }) {
  const color =
    score <= 3 ? "bg-green-100 text-green-800" :
    score <= 6 ? "bg-yellow-100 text-yellow-800" :
    "bg-red-100 text-red-800"

  return (
    <span className={`px-2 py-1 rounded text-sm font-semibold ${color}`}>
      Risk: {score}/10
    </span>
  )
}

export default function App() {
  const [prs, setPrs] = useState<PullRequest[]>([])
  const [selected, setSelected] = useState<PRDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch("/api/prs")
      .then(res => res.json())
      .then(data => {
        setPrs(data)
        setLoading(false)
      })
  }, [])

  function openPR(id: number) {
    fetch(`/api/prs/${id}`)
      .then(res => res.json())
      .then(data => setSelected(data))
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        PR Risk Assistant
      </h1>

      <div className="flex gap-6">
        {/* PR List */}
        <div className="w-1/2 space-y-3">
          <h2 className="text-lg font-semibold text-gray-600">Pull Requests</h2>
          {loading && <p className="text-gray-400">Loading...</p>}
          {prs.map(pr => (
            <div
              key={pr.id}
              onClick={() => openPR(pr.id)}
              className="bg-white rounded-lg p-4 shadow cursor-pointer hover:shadow-md transition"
            >
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-medium text-gray-800">#{pr.pr_number} {pr.title}</p>
                  <p className="text-sm text-gray-500">by {pr.author}</p>
                </div>
                <span className="text-xs text-gray-400">{pr.status}</span>
              </div>
            </div>
          ))}
        </div>

        {/* PR Detail */}
        <div className="w-1/2">
          <h2 className="text-lg font-semibold text-gray-600">Review Detail</h2>
          {!selected && (
            <p className="text-gray-400 mt-4">Click a PR to see its review</p>
          )}
          {selected && (
            <div className="bg-white rounded-lg p-6 shadow space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="font-bold text-gray-800">#{selected.pr_number} {selected.title}</h3>
                {selected.review && <RiskBadge score={selected.review.risk_score} />}
              </div>

              {selected.review ? (
                <>
                  <div>
                    <p className="text-sm font-semibold text-gray-600">Summary</p>
                    <p className="text-gray-700">{selected.review.summary}</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-600">Bugs</p>
                    <p className="text-gray-700">{selected.review.bugs ?? "None found"}</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-600">Security Issues</p>
                    <p className="text-gray-700">{selected.review.security_issues ?? "None found"}</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-600">Test Gaps</p>
                    <p className="text-gray-700">{selected.review.test_gaps ?? "None found"}</p>
                  </div>
                </>
              ) : (
                <p className="text-gray-400">No review available for this PR</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}