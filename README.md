# ✈️ FinPilot AI — Your Personal Finance Copilot

> Built as a Capstone Project for the Agentic Artificial Intelligence program.
FinPilot is an AI-powered financial assistant that actually understands your spending. Upload your expense data, ask it anything in plain English, and it figures out what you need — whether that's a breakdown of where your money went, a prediction for next month, savings tips, or unusual spending alerts.

It doesn't just answer questions. It picks the right tool, runs the analysis, and shows you exactly how it arrived at the answer. That's the agentic part.

---

## What it does

- **Expense Dashboard** — Upload a CSV and instantly see your total spend, category breakdown, and monthly trend with interactive charts
- **Spending Forecast** — Predicts next month's expenses using a blend of Linear Regression and Exponential Moving Average
- **Savings Suggestions** — Gives you 3–5 actionable tips with actual rupee amounts based on your own data, not generic advice
- **Anomaly Detection** — Flags months or categories where your spending spiked statistically (Z-score based)
- **AI Chatbot** — Ask anything. The agent detects your intent, selects the right tool, runs it, and explains the result

---

## How the agent works

```
You type a question
        ↓
LLM Planner reads it and decides which tools to run
        ↓
Tools execute against your actual CSV data
        ↓
LLM Synthesizer turns the results into a clear, specific response
        ↓
You see: Intent → Tools → Reasoning → Answer
```

The whole pipeline is visible in the UI — you can see exactly what the agent is thinking at every step.

---

## Getting started

**1. Clone the repo**
```bash
git clone https://github.com/your-username/finpilot-ai.git
cd finpilot-ai
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your API key**
```bash
cp .env.example .env
# Open .env and paste your OpenRouter API key
```

**4. Run it**
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser, hit **Load Sample Data**, and explore.

> The app works fully without an API key — all charts, tools, predictions, and routing work offline. The API key only powers the AI-generated explanations in the chatbot.

---

## Your CSV format

The app expects a simple CSV with three columns:

```
date,category,amount
2024-01-03,Food,1200
2024-01-07,Transport,450
2024-02-15,Shopping,2800
```

A ready-to-use `sample_data.csv` with 6 months of data is included — just click **Load Sample Data** in the sidebar.

---

## Project structure

```
finpilot/
├── app.py                  # Streamlit UI — hero, dashboard, chatbot
├── agent.py                # The brain — LLM planner, tool router, synthesizer
├── tools/
│   ├── analysis_tool.py    # Breaks down spending by category and month
│   ├── prediction_tool.py  # Forecasts next month (EMA + Linear Regression)
│   ├── suggestion_tool.py  # Generates savings tips from your data
│   └── anomaly_tool.py     # Detects statistical spending spikes (Z-score)
├── utils/
│   └── helpers.py          # CSV validation and currency formatting
├── sample_data.csv         # 60 rows, 6 months, ready to demo
├── requirements.txt
└── .env.example            # Copy this to .env and add your key
```

---

## Tech stack

| Layer | Tools |
|---|---|
| UI | Streamlit, Plotly |
| Data | Pandas, NumPy |
| ML | Scikit-learn (LinearRegression) |
| Statistics | NumPy (Z-score, EMA) |
| AI / LLM | OpenRouter API (GPT-3.5-Turbo via REST) |
| Config | python-dotenv |

 No heavy frameworks. Every component is plain Python and easy to read.

--

## Getting an API key

This project uses [OpenRouter](https://openrouter.ai) which gives you access to GPT-3.5-Turbo and many other models through a single API.

1. Sign up at [openrouter.ai](https://openrouter.ai)
2. Go to **Keys** → Create a new key
3. Paste it into your `.env` file as `OPENROUTER_API_KEY=sk-or-v1-...`

The free tier is enough to run this project comfortably.

---

## Sample questions to try

Once data is loaded, try asking the chatbot:

- *"Where am I overspending?"*
- *"Predict my expenses for next month"*
- *"How can I save money?"*
- *"Did I have any unusual expenses?"*
- *"What's my biggest spending category?"*

---

## Academic context

This project was built as a capstone demonstrating **simple agentic AI** — specifically:

- Intent detection (LLM-based with keyword fallback)
- Tool routing (4 distinct tools, selected dynamically)
- Real data science (ML, statistics, not just LLM calls)
- Transparent execution pipeline visible in the UI

The goal was to show that agentic AI doesn't require complex frameworks — just clear thinking about what a tool is and when to use it.

---

*Built with Python, Streamlit.
