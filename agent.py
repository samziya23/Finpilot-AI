# agent.py
# FinPilot AI — Agentic Core Logic
# LLM-based planner: intent detection, dynamic tool selection, multi-step reasoning, synthesis

import os
import sys
import json

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import requests
import pandas as pd
from dotenv import load_dotenv

from tools.analysis_tool import expense_analysis_tool, format_analysis_summary
from tools.prediction_tool import prediction_tool, format_prediction_summary
from tools.suggestion_tool import savings_suggestion_tool, format_suggestions_summary
from tools.anomaly_tool import anomaly_detection_tool, format_anomaly_summary

load_dotenv()

# ─────────────────────────────────────────────
# TOOL REGISTRY
# Maps tool names (LLM-parseable) to actual functions
# ─────────────────────────────────────────────

TOOL_REGISTRY = {
    "expense_analysis": expense_analysis_tool,
    "spending_prediction": prediction_tool,
    "savings_suggestions": savings_suggestion_tool,
    "anomaly_detection": anomaly_detection_tool,
}

TOOL_DESCRIPTIONS = """
Available tools (call these by exact name):
1. expense_analysis     — Breaks down total spend, monthly trends, category totals, top category, spending trend direction.
2. spending_prediction  — Predicts next month's expenses using weighted moving average + linear regression. Returns prediction, confidence score, change %.
3. savings_suggestions  — Identifies overspending categories relative to the user's own historical average. Returns data-driven % savings insights.
4. anomaly_detection    — Detects months or categories with statistically abnormal spending (>1.5 standard deviations). Returns flagged anomalies.
"""

# ─────────────────────────────────────────────
# 1. RAW LLM CALL (via OpenRouter)
# ─────────────────────────────────────────────

def call_llm(system_prompt: str, user_message: str, max_tokens: int = 600, temperature: float = 0.3) -> str:
    """
    Call OpenRouter API (openai/gpt-3.5-turbo).
    Returns the raw text response, or an error string.
    """
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()

    if not api_key or api_key == "your_openrouter_api_key_here":
        return "__NO_API_KEY__"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://finpilot.ai",
        "X-Title": "FinPilot AI",
    }
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    except requests.exceptions.Timeout:
        return "__TIMEOUT__"
    except requests.exceptions.HTTPError as e:
        return f"__HTTP_ERROR__: {e}"
    except Exception as e:
        return f"__ERROR__: {e}"


# ─────────────────────────────────────────────
# 2. PLANNER — LLM decides tools + reasoning
# ─────────────────────────────────────────────

PLANNER_SYSTEM = f"""You are the planning brain of FinPilot, a financial AI agent.

Your job is to analyze the user's question and produce a concise execution plan.

{TOOL_DESCRIPTIONS}

You MUST respond ONLY with valid JSON (no markdown, no explanation outside JSON):
{{
  "intent": "One short sentence describing the user's goal.",
  "tools": ["tool_name_1", "tool_name_2"],
  "reasoning": [
    "Step 1: Why this tool was chosen.",
    "Step 2: What insight it provides."
  ]
}}

Rules:
- Pick 1-3 tools that best answer the query.
- If the query is multi-part (e.g. "analyze my spending AND give saving tips"), pick multiple tools.
- "reasoning" must have one entry per tool — keep each step under 15 words.
- If the question is entirely off-topic (greetings, non-finance), use tools: [] and explain in intent.
"""

def plan_execution(user_query: str) -> dict:
    """
    Ask the LLM to produce a structured execution plan.
    Returns a dict with: intent, tools (list), reasoning (list).
    Falls back to keyword heuristic if LLM is unavailable.
    """
    raw = call_llm(PLANNER_SYSTEM, f'User question: "{user_query}"', max_tokens=300, temperature=0.2)

    # --- LLM Fallback: keyword heuristic ---
    if raw.startswith("__"):
        return _keyword_fallback(user_query, llm_error=raw)

    # --- Parse JSON from LLM ---
    try:
        # Strip markdown code fences if LLM wraps in them
        clean = raw.strip().strip("```json").strip("```").strip()
        plan = json.loads(clean)

        # Validate and sanitize tool names
        valid_tools = [t for t in plan.get("tools", []) if t in TOOL_REGISTRY]
        return {
            "intent": plan.get("intent", "Analyze user finances."),
            "tools": valid_tools,
            "reasoning": plan.get("reasoning", [f"Running {t}" for t in valid_tools]),
            "llm_driven": True,
        }
    except (json.JSONDecodeError, KeyError):
        return _keyword_fallback(user_query, llm_error="JSON parse failed")


def _keyword_fallback(user_query: str, llm_error: str = "") -> dict:
    """Keyword-based fallback when LLM is unavailable."""
    q = user_query.lower()
    tools, reasoning = [], []

    if any(k in q for k in ["predict", "next month", "forecast", "future", "will i spend"]):
        tools.append("spending_prediction")
        reasoning.append("Query asks about future spending — running prediction tool.")
    if any(k in q for k in ["save", "saving", "reduce", "cut", "tips", "suggestion", "budget"]):
        tools.append("savings_suggestions")
        reasoning.append("Query requests savings advice — running suggestions tool.")
    if any(k in q for k in ["anomaly", "unusual", "spike", "outlier", "abnormal", "weird"]):
        tools.append("anomaly_detection")
        reasoning.append("Query flags unusual spending — running anomaly detector.")
    if any(k in q for k in ["spending", "where", "how much", "analysis", "breakdown", "categories", "pattern"]):
        tools.append("expense_analysis")
        reasoning.append("Query needs spending breakdown — running analysis tool.")

    if not tools:
        tools = ["expense_analysis"]
        reasoning = ["General financial query — defaulting to spending overview."]

    no_key_note = " (LLM offline — using keyword routing)" if "__NO_API_KEY__" in llm_error else ""
    return {
        "intent": f"Answer user's financial query{no_key_note}.",
        "tools": tools,
        "reasoning": reasoning,
        "llm_driven": False,
    }


# ─────────────────────────────────────────────
# 3. TOOL EXECUTOR
# ─────────────────────────────────────────────

def execute_tools(tools: list, df: pd.DataFrame) -> dict:
    """
    Execute each tool by name against the dataframe.
    Returns a dict: {tool_name: tool_result_dict}
    """
    results = {}
    for tool_name in tools:
        func = TOOL_REGISTRY.get(tool_name)
        if func:
            try:
                results[tool_name] = func(df)
            except Exception as e:
                results[tool_name] = {"error": str(e)}
    return results


# ─────────────────────────────────────────────
# 4. RESPONSE SYNTHESIZER
# ─────────────────────────────────────────────

SYNTHESIZER_SYSTEM = """You are FinPilot, a sharp, professional AI financial advisor.

You will receive:
- The user's question
- Concrete financial data extracted from their transaction history

Your job is to synthesize a clear, data-driven financial response.

STRICT OUTPUT FORMAT (use these exact markdown headings):
**💡 Insight:**
[2–3 sentences. Always cite specific numbers (₹, %, months). Be concrete, not generic.]

**📋 Recommendation:**
[1–2 actionable steps the user can take. Be specific.]

**💰 Savings Potential:**
[Quantify exactly: "Reducing X by Y% can save ₹Z/month." Write N/A only if truly not applicable.]

Rules:
- Never say "reduce food spending" — always say "reduce Food by 20% to save ₹1,200/month"
- Always cite data from the provided tool output
- Keep total response under 200 words
"""

def synthesize_response(user_query: str, tool_results: dict, plan: dict) -> str:
    """
    Final LLM call: synthesize all tool data into a user-facing answer.
    """
    # Build context from all tool results
    tool_summaries = []
    for tool_name, data in tool_results.items():
        if tool_name == "expense_analysis":
            tool_summaries.append(f"[Expense Analysis]\n{format_analysis_summary(data)}")
        elif tool_name == "spending_prediction":
            tool_summaries.append(f"[Spending Prediction]\n{format_prediction_summary(data)}")
        elif tool_name == "savings_suggestions":
            tool_summaries.append(f"[Savings Suggestions]\n{format_suggestions_summary(data)}")
        elif tool_name == "anomaly_detection":
            tool_summaries.append(f"[Anomaly Detection]\n{format_anomaly_summary(data)}")

    combined_data = "\n\n".join(tool_summaries)
    user_message = (
        f'User question: "{user_query}"\n\n'
        f"Financial data from tools:\n{combined_data}\n\n"
        "Provide the structured financial response."
    )

    raw = call_llm(SYNTHESIZER_SYSTEM, user_message, max_tokens=450, temperature=0.5)

    if raw == "__NO_API_KEY__":
        return (
            "⚠️ *AI explanation unavailable* — no OpenRouter API key configured.\n\n"
            "The data analysis above is fully accurate.\n"
            "To enable AI synthesis, add your `OPENROUTER_API_KEY` to the `.env` file."
        )
    if raw.startswith("__"):
        return f"⚠️ LLM call failed ({raw}). The tool data above remains valid."

    return raw


# ─────────────────────────────────────────────
# 5. MAIN AGENT ENTRY POINT
# ─────────────────────────────────────────────

def run_agent(user_query: str, df: pd.DataFrame) -> dict:
    """
    Full agentic pipeline:
      1. LLM plans: detects intent + selects tools + reasoning
      2. Execute selected tools against data
      3. LLM synthesizes final response from tool output

    Returns:
        dict with keys:
          - intent         : str
          - tools_used     : list[str]
          - reasoning      : list[str]
          - llm_driven     : bool
          - tool_results   : dict
          - tool_summaries : dict (formatted strings per tool)
          - llm_response   : str
          - chart_data     : dict (for UI rendering)
    """

    # Step 1: Plan
    plan = plan_execution(user_query)

    # Step 2: Execute tools
    tool_results = execute_tools(plan["tools"], df)

    # Step 3: Build formatted summaries
    tool_summaries = {}
    for tool_name, data in tool_results.items():
        if tool_name == "expense_analysis":
            tool_summaries[tool_name] = format_analysis_summary(data)
        elif tool_name == "spending_prediction":
            tool_summaries[tool_name] = format_prediction_summary(data)
        elif tool_name == "savings_suggestions":
            tool_summaries[tool_name] = format_suggestions_summary(data)
        elif tool_name == "anomaly_detection":
            tool_summaries[tool_name] = format_anomaly_summary(data)

    # Step 4: Synthesize
    llm_response = synthesize_response(user_query, tool_results, plan)

    # Step 5: Package chart data for UI
    chart_data = {}
    if "expense_analysis" in tool_results:
        chart_data["analysis"] = tool_results["expense_analysis"]
    if "spending_prediction" in tool_results:
        chart_data["prediction"] = tool_results["spending_prediction"]
    if "anomaly_detection" in tool_results:
        chart_data["anomaly"] = tool_results["anomaly_detection"]

    return {
        "intent": plan["intent"],
        "tools_used": plan["tools"],
        "reasoning": plan["reasoning"],
        "llm_driven": plan["llm_driven"],
        "tool_results": tool_results,
        "tool_summaries": tool_summaries,
        "llm_response": llm_response,
        "chart_data": chart_data,
    }
