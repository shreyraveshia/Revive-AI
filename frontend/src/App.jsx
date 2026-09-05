import { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

const initialRecoveryForm = {
  transaction_id: "dashboard-demo-001",
  amount_paise: 250000,
  payment_method: "upi",
  failure_code: "upi_timeout",
  attempt_number: 1,
  customer_previous_transactions: 8,
  customer_previous_success_rate: 0.67,
  customer_previous_avg_amount_paise: 210000,
  merchant_previous_transactions: 120,
  merchant_previous_success_rate: 0.91,
  merchant_previous_avg_amount_paise: 195000,
};

function formatRupees(paise) {
  return `₹${(paise / 100).toLocaleString("en-IN", {
    maximumFractionDigits: 0,
  })}`;
}

function StatCard({ label, value, subtext }) {
  return (
    <div className="stat-card">
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-subtext">{subtext}</div>
    </div>
  );
}

function App() {
  const [metrics, setMetrics] = useState(null);
  const [actions, setActions] = useState([]);
  const [error, setError] = useState("");

  const [form, setForm] = useState(initialRecoveryForm);
  const [decision, setDecision] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      const [metricsResponse, actionsResponse] = await Promise.all([
        fetch(`${API_BASE}/api/metrics`),
        fetch(`${API_BASE}/api/recovery/actions`),
      ]);

      if (!metricsResponse.ok || !actionsResponse.ok) {
        throw new Error("Failed to load dashboard data");
      }

      const metricsData = await metricsResponse.json();
      const actionsData = await actionsResponse.json();

      setMetrics(metricsData);
      setActions(actionsData);
      setError("");
    } catch (err) {
      setError(err.message);
    }
  }

  function updateForm(field, value) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function analyzeRecovery(event) {
    event.preventDefault();

    setAnalyzing(true);
    setError("");
    setDecision(null);

    try {
      const response = await fetch(`${API_BASE}/api/recovery/decide`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...form,
          amount_paise: Number(form.amount_paise),
          attempt_number: Number(form.attempt_number),
          customer_previous_transactions: Number(
            form.customer_previous_transactions,
          ),
          customer_previous_success_rate: Number(
            form.customer_previous_success_rate,
          ),
          customer_previous_avg_amount_paise: Number(
            form.customer_previous_avg_amount_paise,
          ),
          merchant_previous_transactions: Number(
            form.merchant_previous_transactions,
          ),
          merchant_previous_success_rate: Number(
            form.merchant_previous_success_rate,
          ),
          merchant_previous_avg_amount_paise: Number(
            form.merchant_previous_avg_amount_paise,
          ),
        }),
      });

      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(body?.detail || "Recovery analysis failed");
      }

      setDecision(await response.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <div className="brand">REVIVE AI</div>
          <div className="brand-subtitle">
            AI-powered revenue recovery engine
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot" />
          System operational
        </div>
      </header>

      <main className="dashboard">
        <section className="hero">
          <p className="eyebrow">REVENUE RECOVERY CONTROL CENTER</p>
          <h1>Recover more revenue with the next best action.</h1>
          <p className="hero-copy">
            Revive detects failed payments, diagnoses the failure, predicts
            recovery outcomes, and selects a bounded intervention.
          </p>
        </section>

        {error && <div className="error-banner">{error}</div>}

        <section className="stats-grid">
          <StatCard
            label="Revenue at Risk"
            value={metrics ? formatRupees(metrics.revenue_at_risk_paise) : "—"}
            subtext={`${metrics?.failed_payments ?? 0} failed payments`}
          />

          <StatCard
            label="Recovered Revenue"
            value={
              metrics ? formatRupees(metrics.recovered_revenue_paise) : "—"
            }
            subtext={`${((metrics?.recovery_rate ?? 0) * 100).toFixed(1)}% recovery rate`}
          />

          <StatCard
            label="Actions Executed"
            value={metrics?.executed_actions ?? "—"}
            subtext="Bounded recovery interventions"
          />

          <StatCard
            label="Recovery Rate"
            value={
              metrics ? `${(metrics.recovery_rate * 100).toFixed(1)}%` : "—"
            }
            subtext="Verified recovery outcomes"
          />
        </section>

        <section className="console-grid">
          <div className="panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">LIVE DECISION ENGINE</p>
                <h2>Analyze failed payment</h2>
              </div>
            </div>

            <form className="recovery-form" onSubmit={analyzeRecovery}>
              <div className="field">
                <label>Transaction ID</label>
                <input
                  value={form.transaction_id}
                  onChange={(e) =>
                    updateForm("transaction_id", e.target.value)
                  }
                />
              </div>

              <div className="form-row">
                <div className="field">
                  <label>Amount (₹)</label>
                  <input
                    type="number"
                    min="1"
                    step="1"
                    value={form.amount_paise / 100}
                    onChange={(e) =>
                      updateForm(
                        "amount_paise",
                        Math.round(Number(e.target.value) * 100),
                      )
                    }
                  />
                </div>

                <div className="field">
                  <label>Payment method</label>
                  <select
                    value={form.payment_method}
                    onChange={(e) =>
                      updateForm("payment_method", e.target.value)
                    }
                  >
                    <option value="upi">UPI</option>
                    <option value="card">Card</option>
                    <option value="netbanking">Netbanking</option>
                    <option value="wallet">Wallet</option>
                  </select>
                </div>
              </div>

              <div className="field">
                <label>Failure reason</label>
                <select
                  value={form.failure_code}
                  onChange={(e) =>
                    updateForm("failure_code", e.target.value)
                  }
                >
                  <option value="upi_timeout">UPI timeout</option>
                  <option value="upi_declined">UPI declined</option>
                  <option value="insufficient_funds">
                    Insufficient funds
                  </option>
                  <option value="soft_decline">Soft decline</option>
                  <option value="hard_decline">Hard decline</option>
                  <option value="network_error">Network error</option>
                  <option value="gateway_error">Gateway error</option>
                  <option value="authentication_failed">
                    Authentication failed
                  </option>
                  <option value="checkout_abandoned">
                    Checkout abandoned
                  </option>
                </select>
              </div>

              <button className="primary-button" type="submit" disabled={analyzing}>
                {analyzing ? "Analyzing..." : "Analyze payment"}
              </button>
            </form>
          </div>

          <div className="panel decision-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">REVIVE DECISION</p>
                <h2>Next-best action</h2>
              </div>
            </div>

            {!decision ? (
              <div className="decision-empty">
                <div className="decision-icon">AI</div>
                <p>
                  Submit a failed payment to run diagnosis, recovery
                  prediction, and policy evaluation.
                </p>
              </div>
            ) : (
              <div className="decision-content">
                <div className="recommendation">
                  <div className="recommendation-label">
                    RECOMMENDED ACTION
                  </div>
                  <div className="recommendation-action">
                    {decision.selected_action.replace("_", " ")}
                  </div>
                  <div className="recommendation-reason">
                    {decision.decision_reason.replaceAll("_", " ")}
                  </div>
                </div>

                <div className="diagnosis-box">
                  <div className="mini-label">AI DIAGNOSIS</div>
                  <div className="diagnosis-title">
                    {decision.diagnosis.likely_cause}
                  </div>
                  <p>{decision.diagnosis.explanation}</p>

                  <div className="diagnosis-meta">
                    <span>
                      Confidence{" "}
                      <strong>
                        {(decision.diagnosis.confidence * 100).toFixed(0)}%
                      </strong>
                    </span>
                    <span>
                      Severity{" "}
                      <strong>{decision.diagnosis.severity}</strong>
                    </span>
                  </div>
                </div>

                <div className="score-list">
                  <div className="mini-label">ACTION EVALUATION</div>

                  {decision.action_scores.map((score) => (
                    <div className="score-row" key={score.action}>
                      <span className="score-action">
                        {score.action.replace("_", " ")}
                      </span>

                      <div className="score-bar">
                        <div
                          className="score-fill"
                          style={{
                            width: `${Math.min(
                              score.recovery_probability * 100,
                              100,
                            )}%`,
                          }}
                        />
                      </div>

                      <span className="score-value">
                        {(score.recovery_probability * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>

                <div className="message-box">
                  <div className="mini-label">CUSTOMER MESSAGE</div>
                  <p>{decision.diagnosis.customer_message}</p>
                </div>
              </div>
            )}
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">RECOVERY QUEUE</p>
              <h2>Recent recovery actions</h2>
            </div>
            <span className="panel-count">{actions.length} actions</span>
          </div>

          {actions.length === 0 ? (
            <div className="empty-state">No recovery actions yet.</div>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Transaction</th>
                    <th>Amount</th>
                    <th>Action</th>
                    <th>Expected Recovery</th>
                    <th>Status</th>
                  </tr>
                </thead>

                <tbody>
                  {actions.map((item) => (
                    <tr key={item.action_id}>
                      <td>
                        <div className="primary-cell">{item.order_id}</div>
                        <div className="secondary-cell">
                          {item.reason}
                        </div>
                      </td>

                      <td>{formatRupees(item.amount_paise)}</td>

                      <td>
                        <span className="action-pill">
                          {item.action.replace("_", " ")}
                        </span>
                      </td>

                      <td>
                        {(item.expected_recovery_probability * 100).toFixed(1)}
                        %
                      </td>

                      <td>
                        <span className="status-pill">{item.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;