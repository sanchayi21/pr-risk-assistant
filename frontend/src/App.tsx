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
  const bg =
    score <= 3 ? "#dcfce7" :
    score <= 6 ? "#fef9c3" :
    "#fee2e2"
  const text =
    score <= 3 ? "#15803d" :
    score <= 6 ? "#a16207" :
    "#b91c1c"
  const label =
    score <= 3 ? "Low Risk" :
    score <= 6 ? "Medium Risk" :
    "High Risk"

  return (
    <span style={{
      backgroundColor: bg,
      color: text,
      padding: "4px 12px",
      borderRadius: 20,
      fontSize: 13,
      fontWeight: 700,
      letterSpacing: 0.3
    }}>
      {label} · {score}/10
    </span>
  )
}

function Section({ label, value }: { label: string; value: string }) {
  return (
    <div style={{
      backgroundColor: "#f8faff",
      borderRadius: 8,
      padding: "12px 16px",
      marginBottom: 10,
      borderLeft: "3px solid #60a5fa"
    }}>
      <p style={{
        fontSize: 11, fontWeight: 700, color: "#3b82f6",
        margin: "0 0 4px", textTransform: "uppercase", letterSpacing: 1
      }}>{label}</p>
      <p style={{ fontSize: 14, color: "#1e293b", margin: 0, lineHeight: 1.6 }}>{value}</p>
    </div>
  )
}

export default function App() {
  const [prs, setPrs] = useState<PullRequest[]>([])
  const [selected, setSelected] = useState<PRDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedId, setSelectedId] = useState<number | null>(null)

  useEffect(() => {
    fetch("https://pr-risk-assistant.onrender.com/prs")
      .then(res => res.json())
      .then(data => { setPrs(data); setLoading(false) })
  }, [])

  function openPR(id: number) {
    setSelectedId(id)
    fetch(`https://pr-risk-assistant.onrender.com/prs/${id}`)
      .then(res => res.json())
      .then(data => setSelected(data))
  }

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#f0f6ff", fontFamily: "'Segoe UI', system-ui, sans-serif" }}>

      {/* Header */}
      <div style={{
      background: "linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%)",        padding: "28px 40px",
        textAlign: "center",
        boxShadow: "0 4px 20px rgba(59,130,246,0.15)"
      }}>
        <h1 style={{
          margin: 0, fontSize: 24, fontWeight: 700,
          color: "white", letterSpacing: 0.5
        }}>
          🔍 PR Risk Assistant
        </h1>
        <p style={{ margin: "6px 0 0", fontSize: 13, color: "rgba(255,255,255,0.8)" }}>
          AI-powered code review for every pull request
        </p>
      </div>

      {/* Main Content */}
      <div style={{
        display: "flex", gap: 20, padding: "28px 40px",
        maxWidth: 1200, margin: "0 auto"
      }}>

        {/* PR List */}
        <div style={{ width: "45%" }}>
          <div style={{
            display: "flex", justifyContent: "space-between",
            alignItems: "center", marginBottom: 14
          }}>
            <h2 style={{ margin: 0, fontSize: 15, fontWeight: 700, color: "#334155" }}>
              Pull Requests
            </h2>
            <span style={{
              backgroundColor: "#dbeafe", color: "#1d4ed8",
              padding: "2px 10px", borderRadius: 12,
              fontSize: 12, fontWeight: 600
            }}>
              {prs.length} total
            </span>
          </div>

          {loading && (
            <div style={{ textAlign: "center", padding: 40, color: "#94a3b8" }}>
              Loading pull requests...
            </div>
          )}

          {prs.map(pr => (
            <div
              key={pr.id}
              onClick={() => openPR(pr.id)}
              style={{
                backgroundColor: selectedId === pr.id ? "#eff6ff" : "white",
                borderRadius: 10,
                padding: "14px 16px",
                marginBottom: 10,
                cursor: "pointer",
                boxShadow: selectedId === pr.id
                  ? "0 0 0 2px #3b82f6, 0 2px 8px rgba(0,0,0,0.06)"
                  : "0 1px 4px rgba(0,0,0,0.07)",
                borderLeft: `4px solid ${selectedId === pr.id ? "#3b82f6" : "#e2e8f0"}`,
                transition: "all 0.15s ease"
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div style={{ flex: 1 }}>
                  <p style={{ margin: "0 0 4px", fontWeight: 600, fontSize: 14, color: "#0f172a" }}>
                    <span style={{ color: "#3b82f6" }}>#{pr.pr_number}</span> {pr.title}
                  </p>
                  <p style={{ margin: 0, fontSize: 12, color: "#64748b" }}>
                    by {pr.author} · {new Date(pr.created_at).toLocaleDateString()}
                  </p>
                </div>
                <span style={{
                  fontSize: 11, fontWeight: 600,
                  backgroundColor: pr.status === "open" ? "#dcfce7" : "#f1f5f9",
                  color: pr.status === "open" ? "#15803d" : "#64748b",
                  padding: "2px 8px", borderRadius: 10,
                  marginLeft: 8, whiteSpace: "nowrap"
                }}>
                  {pr.status}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Review Detail */}
        <div style={{ width: "55%" }}>
          <h2 style={{ margin: "0 0 14px", fontSize: 15, fontWeight: 700, color: "#334155" }}>
            Review Detail
          </h2>

          {!selected && (
            <div style={{
              backgroundColor: "white", borderRadius: 10, padding: 40,
              textAlign: "center", boxShadow: "0 1px 4px rgba(0,0,0,0.07)"
            }}>
              <p style={{ color: "#94a3b8", margin: 0, fontSize: 14 }}>
                Select a pull request to see its AI review
              </p>
            </div>
          )}

          {selected && (
            <div style={{
              backgroundColor: "white", borderRadius: 10,
              boxShadow: "0 1px 4px rgba(0,0,0,0.07)", overflow: "hidden"
            }}>
              {/* Detail Header */}
              <div style={{
                background: "linear-gradient(135deg, #3b82f6, #93c5fd)",
                padding: "16px 20px",
                display: "flex", justifyContent: "space-between", alignItems: "center"
              }}>
                <div>
                  <p style={{ margin: 0, fontSize: 13, color: "rgba(255,255,255,0.8)" }}>
                    PR #{selected.pr_number}
                  </p>
                  <p style={{ margin: "2px 0 0", fontSize: 15, fontWeight: 700, color: "white" }}>
                    {selected.title}
                  </p>
                </div>
                {selected.review && <RiskBadge score={selected.review.risk_score} />}
              </div>

              {/* Detail Body */}
              <div style={{ padding: 20 }}>
                {selected.review ? (
                  <>
                    <Section label="Summary" value={selected.review.summary} />
                    <Section label="Bugs Found" value={selected.review.bugs ?? "✅ No bugs found"} />
                    <Section label="Security Issues" value={selected.review.security_issues ?? "✅ No security issues"} />
                    <Section label="Test Gaps" value={selected.review.test_gaps ?? "✅ No test gaps identified"} />
                  </>
                ) : (
                  <p style={{ color: "#94a3b8", textAlign: "center", padding: 20 }}>
                    No review available for this PR
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}