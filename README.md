Absolutely. Since this is the **final GitHub README for the Buildathon**, I’d make it judge-oriented: clear problem, architecture, AI/ML approach, safety, Razorpay integration, evaluation, setup, and demo flow.

Replace the entire root `README.md` with this:

````markdown
# Revive AI

### AI-Powered Revenue Recovery & Next-Best-Action Engine

Revive AI is an intelligent revenue recovery engine designed to recover revenue lost from failed digital payments.

Instead of applying the same retry strategy to every failure, Revive analyzes the payment context, diagnoses the likely cause, predicts the probability of recovery for multiple interventions, and selects the economically optimal next-best action while enforcing deterministic safety and governance rules.

> **Probabilistic intelligence, deterministic money movement.**

---

## Problem

Payment failures do not all have the same cause or the same recovery path.

A UPI timeout may be recoverable through a retry, while insufficient funds may require a reminder, and an abandoned checkout may be better recovered through a Payment Link.

A naive recovery system may:

- retry blindly,
- use the same intervention for every failure,
- create unnecessary customer friction,
- waste recovery opportunities,
- or allow an AI model to make unrestricted financial decisions.

Revive AI treats revenue recovery as a **decision optimization problem** rather than simply a payment retry problem.

---

## Solution

Revive AI follows an end-to-end recovery loop:

```text
Detect
  ↓
Diagnose
  ↓
Predict
  ↓
Optimize
  ↓
Govern
  ↓
Intervene
  ↓
Verify
  ↓
Quantify
  ↓
Learn
````

For every failed payment, Revive combines:

1. **LLM-based diagnosis** to understand the likely failure cause.
2. **Machine learning** to estimate recovery probability for multiple actions.
3. **Expected-value optimization** to choose the economically strongest option.
4. **Deterministic policy controls** to enforce safety, retry limits, eligibility, and execution boundaries.
5. **Bounded execution** through supported recovery mechanisms.
6. **Webhook-based verification** to determine whether revenue was actually recovered.
7. **Persistent audit records** for recovery actions and outcomes.

---

# Core Architecture

```text
                         ┌──────────────────────┐
                         │    Failed Payment    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   FastAPI API Layer  │
                         └──────────┬───────────┘
                                    │
                   ┌────────────────┴────────────────┐
                   │                                 │
                   ▼                                 ▼
        ┌────────────────────┐            ┌────────────────────┐
        │   LLM Diagnosis    │            │  Historical Data   │
        │       Groq         │            │ Customer/Merchant  │
        └──────────┬─────────┘            └──────────┬─────────┘
                   │                                 │
                   │                                 ▼
                   │                       ┌────────────────────┐
                   │                       │ LightGBM Recovery  │
                   │                       │ Probability Model  │
                   │                       └──────────┬─────────┘
                   │                                  │
                   └────────────────┬─────────────────┘
                                    ▼
                         ┌──────────────────────┐
                         │ Expected Value       │
                         │ Action Optimization  │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │ Deterministic Policy │
                         │ & Guardrails         │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │   RecoveryAction     │
                         │   Audit + Idempotency│
                         └──────────┬───────────┘
                                    │
                  ┌─────────────────┴──────────────────┐
                  │                                    │
                  ▼                                    ▼
           Simulation-only                        Executable
             actions                               actions
                  │                                    │
                  │                                    ▼
                  │                         ┌────────────────────┐
                  │                         │ Razorpay Test Mode│
                  │                         │   Payment Link     │
                  │                         └──────────┬─────────┘
                  │                                    │
                  │                                    ▼
                  │                         ┌────────────────────┐
                  │                         │ payment_link.paid  │
                  │                         │ Webhook            │
                  │                         └──────────┬─────────┘
                  │                                    │
                  └────────────────┬───────────────────┘
                                   ▼
                         ┌──────────────────────┐
                         │ RecoveryOutcome      │
                         │ Verified Revenue     │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │ React Dashboard      │
                         │ Metrics + Decisions  │
                         └──────────────────────┘
```

---

# Key Design Principle

## Probabilistic intelligence, deterministic money movement

LLMs and ML models are useful for reasoning under uncertainty, but they should not have unrestricted authority over financial actions.

Revive therefore separates the system into two layers.

### Probabilistic layer

The AI/ML components:

* diagnose payment failures,
* estimate recovery probabilities,
* rank possible interventions,
* generate customer-facing explanations.

### Deterministic layer

The policy and execution components:

* enforce eligibility,
* enforce retry limits,
* enforce economic thresholds,
* prevent duplicate execution,
* validate external references,
* control supported actions,
* verify recovery outcomes.

This means the AI can recommend an action, but deterministic code decides whether that action is actually allowed to execute.

---

# Supported Recovery Actions

Revive evaluates the following action space:

| Action             | Description                          |
| ------------------ | ------------------------------------ |
| `NO_ACTION`        | Do not intervene                     |
| `RETRY`            | Retry the payment in the simulator   |
| `ALTERNATE_METHOD` | Encourage a different payment method |
| `PAYMENT_LINK`     | Generate a payment link              |
| `REMINDER`         | Send a recovery reminder             |
| `ESCALATE`         | Escalate the recovery case           |

For the live Razorpay integration, the implementation currently supports **Payment Link execution**.

Retry and other non-integrated actions remain simulation-oriented rather than pretending unsupported external APIs exist.

---

# AI & ML Pipeline

## 1. Failure diagnosis

Revive uses an LLM through a provider abstraction.

The diagnosis includes:

* likely cause,
* severity,
* confidence,
* explanation,
* recommended recovery focus,
* customer-facing message.

The LLM output is validated with a strict Pydantic schema.

A deterministic fallback diagnosis is used when the LLM is unavailable.

---

## 2. Recovery probability prediction

The recovery model estimates:

```text
P(recovery | transaction context, failure, action)
```

Features include:

### Transaction

* payment amount
* payment method
* failure code
* attempt number

### Customer history

* previous transaction count
* historical success rate
* historical average transaction amount

### Merchant history

* previous transaction count
* historical success rate
* historical average transaction amount

### Candidate action

* retry
* alternate payment method
* payment link
* reminder
* no action
* escalation

---

# Data Leakage Prevention

A major modeling requirement was avoiding information from the current transaction outcome leaking into its own prediction.

The synthetic payment world therefore generates transactions chronologically.

For each transaction, historical features are calculated using only information available **before the current payment attempt**.

The current transaction outcome is only added to the customer's and merchant's history **after** the transaction is generated.

The train, validation, and test sets are split by transaction rather than by individual recovery-action rows, preventing the same transaction from appearing across multiple splits.

---

# Model Evaluation

The project evaluates multiple strategies inside the controlled synthetic recovery environment.

### LightGBM recovery model

| Metric   | Validation |  Test |
| -------- | ---------: | ----: |
| ROC-AUC  |      0.735 | 0.734 |
| PR-AUC   |      0.522 | 0.515 |
| Log Loss |      0.536 | 0.532 |

### Recovery strategy comparison

| Strategy      | Recovery Rate |
| ------------- | ------------: |
| No Action     |         6.22% |
| Blind Retry   |        32.49% |
| Simple Rules  |        53.61% |
| **Revive ML** |    **53.94%** |

These figures come from the project's synthetic evaluation environment and are intended to compare strategies consistently, not to claim production payment performance.

---

# Economic Decisioning

Revive does not simply choose the action with the highest raw probability.

For every action:

```text
Expected Value
=
Probability of Recovery × Transaction Value
− Action Cost
− Friction Cost
− Risk Cost
```

The policy engine then evaluates the candidate actions against deterministic rules.

This allows the system to balance:

* expected recovered revenue,
* customer friction,
* action cost,
* financial risk,
* retry limits,
* eligibility constraints.

---

# Governance & Safety

Revive implements deterministic safety controls around AI recommendations.

Examples include:

* maximum retry attempts,
* blocked retry scenarios,
* economic minimum thresholds,
* escalation rules,
* idempotency protection,
* execution-state tracking,
* webhook signature verification,
* duplicate webhook protection.

A recovery action receives a persistent idempotency key, preventing repeated analysis from creating unlimited duplicate actions.

External execution is also blocked when a recovery action already has an external reference.

---

# Razorpay Integration

Revive integrates with Razorpay Test Mode for bounded Payment Link recovery.

The execution flow is:

```text
RecoveryAction
      ↓
Policy allows execution
      ↓
Razorpay Payment Link API
      ↓
Payment Link created
      ↓
external_reference stored
      ↓
Customer completes payment
      ↓
payment_link.paid webhook
      ↓
Webhook signature verified
      ↓
RecoveryOutcome created
      ↓
Transaction marked recovered
      ↓
Dashboard metrics updated
```

### Reliability controls

The webhook handler:

* verifies the Razorpay signature,
* stores webhook event IDs,
* ignores duplicate events,
* matches the external Payment Link reference,
* creates exactly one recovery outcome,
* records the recovered amount.

---

# Current Live Demo Flow

The dashboard demonstrates the complete system using a fresh synthetic failed payment.

Example:

```text
Transaction
₹2,500
UPI
Checkout abandoned
```

Revive then produces:

```text
AI Diagnosis
        ↓
Recovery probabilities
        ↓
Expected-value optimization
        ↓
PAYMENT_LINK
        ↓
Razorpay Test Mode
        ↓
Payment Link created
        ↓
payment_link.paid webhook
        ↓
RecoveryOutcome
        ↓
₹2,500 recovered
```

The React dashboard exposes this decision process interactively.

---

# Dashboard

The frontend provides:

### Operational metrics

* Revenue at Risk
* Recovered Revenue
* Actions Executed
* Recovery Rate / Recovery Yield

### Recovery Funnel

```text
Revenue at Risk
      ↓
Recovery Actions
      ↓
Recovered Revenue
```

### Decision Mix

Displays the types of next-best actions selected by Revive.

### Live Decision Engine

A failed payment can be submitted directly through the dashboard to trigger:

```text
LLM diagnosis
+
ML prediction
+
policy evaluation
```

### Execution Control

The UI distinguishes between:

* executable Payment Link recovery,
* simulation-only actions.

---

# Tech Stack

## Backend

* Python 3.12
* FastAPI
* Pydantic 2
* SQLAlchemy 2
* PostgreSQL
* Alembic
* httpx

## Machine Learning

* pandas
* NumPy
* scikit-learn
* LightGBM
* joblib

## LLM

* Groq
* Provider abstraction
* Structured Pydantic output validation

## Frontend

* React
* Vite
* JavaScript
* Recharts
* CSS

## Payments

* Razorpay Test Mode
* Payment Links
* Webhook verification

---

# Project Structure

```text
Revive-AI/
│
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   ├── api/
│   │   ├── decision/
│   │   ├── domain/
│   │   ├── executor/
│   │   ├── llm/
│   │   ├── ml/
│   │   ├── models/
│   │   ├── policy/
│   │   ├── simulation/
│   │   ├── webhooks/
│   │   └── main.py
│   │
│   ├── artifacts/
│   │   ├── recovery_model.joblib
│   │   └── recovery_features.txt
│   │
│   ├── alembic/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── data/
│   ├── raw/
│   └── processed/
│
├── scripts/
│   ├── generate_dataset.py
│   ├── evaluate_baselines.py
│   ├── evaluate_rules.py
│   ├── evaluate_revive.py
│   ├── diagnose_revive.py
│   ├── test_webhook_endpoint.py
│   ├── test_payment_link_paid.py
│   └── ...
│
├── tests/
│
├── docs/
├── .env.example
├── .gitignore
└── README.md
```

---

# Local Setup

## Prerequisites

* Python 3.12
* PostgreSQL
* Node.js / npm
* Razorpay Test Mode credentials
* Groq API key

---

## 1. Clone

```bash
git clone https://github.com/shreyraveshia/Revive-AI.git
cd Revive-AI
```

---

## 2. Backend environment

Create and activate a virtual environment:

```bash
python -m venv .venv
```

### Windows

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

---

## 3. Environment variables

Create `.env` in the project root based on `.env.example`.

Example:

```env
ENVIRONMENT=development

DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/revive_ai

GROQ_API_KEY=your_groq_api_key

RAZORPAY_KEY_ID=your_razorpay_test_key_id
RAZORPAY_KEY_SECRET=your_razorpay_test_key_secret
RAZORPAY_WEBHOOK_SECRET=your_razorpay_webhook_secret
```

Never commit real credentials.

---

## 4. Database

Create the PostgreSQL database:

```sql
CREATE DATABASE revive_ai;
```

Apply migrations:

```bash
cd backend
alembic upgrade head
```

---

## 5. Run backend

From `backend/`:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
GET /health
```

Database health:

```text
GET /health/db
```

---

# API Overview

## Dashboard

```http
GET /api/metrics
GET /api/recovery/actions
```

## Recovery decision

```http
POST /api/recovery/decide
```

Runs the:

```text
LLM
→ ML
→ economic optimization
→ deterministic policy
```

pipeline and persists the resulting `RecoveryAction`.

## Recovery execution

```http
POST /api/recovery/execute
```

Currently supports bounded Payment Link execution.

## Razorpay webhook

```http
POST /webhooks/razorpay
```

Handles verified `payment_link.paid` events.

## Demo transaction

```http
POST /api/demo/failed-payment
```

Creates a synthetic failed transaction for demonstration/testing.

---

# Frontend Setup

From the project root:

```bash
cd frontend
npm install
npm run dev
```

The Vite frontend is typically available at:

```text
http://localhost:5173
```

Build for production:

```bash
npm run build
```

---

# Example Decision

For a checkout abandonment:

```text
Amount: ₹2,500
Payment Method: UPI
Failure: checkout_abandoned
```

Revive can evaluate:

```text
Payment Link     66.8%
Reminder         50.7%
Alternate       24.9%
Retry           13.2%
```

and select:

```text
PAYMENT_LINK
```

based on expected value and policy eligibility.

---

# Why Revive AI?

Traditional payment recovery often asks:

> "Should we retry this payment?"

Revive asks:

> "Given this customer's history, merchant context, failure cause, transaction value, and available interventions, what is the economically optimal and policy-compliant next action?"

That changes revenue recovery from a static retry mechanism into an **adaptive decision system**.

---

# Build Challenges

The project involved several technical challenges:

### AI safety

The LLM needed to provide useful reasoning without directly controlling financial execution.

**Solution:** separate LLM/ML recommendation from deterministic policy and execution layers.

### Data leakage

Current transaction outcomes must not leak into their own recovery prediction.

**Solution:** generate transactions chronologically and construct historical features using only prior events.

### Multiple recovery strategies

Different failures require different interventions.

**Solution:** model recovery probability for each candidate action and optimize expected value rather than selecting a single fixed strategy.

### Razorpay reliability

Payment execution must be safe against duplicate actions and duplicate webhook events.

**Solution:** persistent RecoveryAction records, idempotency keys, external-reference checks, webhook signature verification, and unique event handling.

### Frontend/backend integration

The React frontend initially could not communicate with FastAPI because of cross-origin restrictions.

**Solution:** explicitly configured FastAPI CORS for the local development origins.

### Database/API consistency

SQLAlchemy enum serialization caused differences between database values and API expectations.

**Solution:** normalized API responses and used database-compatible comparisons for metrics.

---

# Limitations & Future Work

Revive is currently a Buildathon MVP and intentionally uses a modular monolith architecture.

Potential future extensions include:

* production payment-retry integrations,
* larger real-world training datasets,
* online model monitoring,
* action-level experimentation,
* merchant-specific policies,
* customer segmentation,
* multilingual recovery messaging,
* voice-based recovery workflows,
* automated campaign scheduling,
* richer recovery analytics,
* production-grade authentication and authorization.

The current ML evaluation uses a synthetic payment environment, so its performance metrics should be interpreted as controlled strategy comparisons rather than production forecasts.

---

# Demo Highlights

The current implementation demonstrates:

* AI-powered payment failure diagnosis
* ML-based recovery probability prediction
* Expected-value next-best-action selection
* Deterministic governance and safety controls
* Persistent recovery action audit trail
* Razorpay Test Mode Payment Link execution
* Webhook signature verification
* Duplicate webhook protection
* Verified recovery outcomes
* Live revenue recovery dashboard

---

# Project Philosophy

Revive AI is built around a simple principle:

> **AI should optimize the decision. Deterministic systems should control the money.**

The goal is not to make an LLM responsible for payments.

The goal is to use AI where uncertainty and reasoning matter, while keeping financial execution bounded, auditable, idempotent, and deterministic.

---

# Author

**Shrey Raveshia**

Built for the **Razorpay AI Buildathon 2026**.

---

````

### One thing I would do immediately

After replacing `README.md`, run:

```powershell
cd E:\revive-ai
git add README.md
git commit -m "docs: finalize project README"
git push origin main
git status
````

That should be your **final documentation checkpoint** before submitting the Google Form.
