"""
Minimal Flask web app to run TradingAgents analyses.

Endpoints:
- GET /               -> simple form UI to run an analysis
- POST /api/analyze   -> run TradingAgentsGraph.propagate(ticker, trade_date)

How provider/model is selected:
- If GROQ_API_KEY is set -> use OpenAI-compatible client with Groq backend and llama-3.1-8b-instant
- Else if OPENAI_API_KEY -> use OpenAI backend and default models from DEFAULT_CONFIG
- Else if ANTHROPIC_API_KEY -> use Anthropic provider
- Else if GOOGLE_API_KEY -> use Google provider
- Else -> return 400 asking for an API key
"""

from __future__ import annotations

import os
import sys
import json
from datetime import date
from typing import Any, Dict

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

# Ensure project root is in sys.path (so we can import tradingagents/*)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Load .env from project root if present
load_dotenv(os.path.join(PROJECT_ROOT, ".env"), override=False)

from tradingagents.default_config import DEFAULT_CONFIG  # type: ignore
from tradingagents.graph.trading_graph import TradingAgentsGraph  # type: ignore


app = Flask(__name__, template_folder="templates", static_folder="static")


def _has_nonempty_env(var: str) -> bool:
    v = os.getenv(var)
    return bool(v and str(v).strip())


def build_config(user_config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Compose runtime config based on environment and optional overrides.

    Selection priority for provider:
    - GROQ_API_KEY -> provider=openai (OpenAI-compatible), backend_url Groq
    - OPENAI_API_KEY -> provider=openai
    - ANTHROPIC_API_KEY -> provider=anthropic
    - GOOGLE_API_KEY -> provider=google
    """
    cfg = DEFAULT_CONFIG.copy()

    user_config = user_config or {}

    # Prefer Groq if present (and non-empty)
    if _has_nonempty_env("GROQ_API_KEY"):
        cfg.update(
            {
                "llm_provider": "openai",  # Groq is OpenAI-compatible
                "quick_think_llm": "llama-3.1-8b-instant",
                "deep_think_llm": "llama-3.1-8b-instant",
                "backend_url": "https://api.groq.com/openai/v1",
                # The client reads OPENAI_API_KEY var by default; map from GROQ if missing
            }
        )
        # If OPENAI_API_KEY is not set, mirror GROQ_API_KEY for OpenAI-compatible clients
        os.environ.setdefault("OPENAI_API_KEY", os.getenv("GROQ_API_KEY", ""))
    elif _has_nonempty_env("OPENAI_API_KEY"):
        cfg.update({"llm_provider": "openai", "backend_url": cfg.get("backend_url", "https://api.openai.com/v1")})
    elif _has_nonempty_env("ANTHROPIC_API_KEY"):
        cfg.update({
            "llm_provider": "anthropic",
            # Sensible defaults if not overridden
            "quick_think_llm": user_config.get("quick_think_llm", "claude-3-5-sonnet-20240620"),
            "deep_think_llm": user_config.get("deep_think_llm", "claude-3-5-sonnet-20240620"),
            "backend_url": user_config.get("backend_url", "https://api.anthropic.com"),
        })
    elif _has_nonempty_env("GOOGLE_API_KEY"):
        cfg.update({
            "llm_provider": "google",
            "quick_think_llm": user_config.get("quick_think_llm", "gemini-1.5-flash"),
            "deep_think_llm": user_config.get("deep_think_llm", "gemini-1.5-pro"),
        })
    else:
        # No provider keys found; keep defaults but signal the caller
        cfg["__no_provider__"] = True

    # Merge user overrides last
    cfg.update(user_config)
    return cfg


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/env")
def env_info():
    # Minimal diagnostics to help debug provider selection
    info = {
        "has_GROQ_API_KEY": bool(os.getenv("GROQ_API_KEY")),
        "has_OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        "has_ANTHROPIC_API_KEY": bool(os.getenv("ANTHROPIC_API_KEY")),
        "has_GOOGLE_API_KEY": bool(os.getenv("GOOGLE_API_KEY")),
    }
    # Show planned provider from a dry build_config
    cfg = build_config({})
    info.update({
        "provider": cfg.get("llm_provider"),
        "backend_url": cfg.get("backend_url"),
        "quick_think_llm": cfg.get("quick_think_llm"),
        "deep_think_llm": cfg.get("deep_think_llm"),
        "no_provider_flag": bool(cfg.get("__no_provider__")),
    })
    return jsonify(info)


@app.post("/api/analyze")
def api_analyze():
    try:
        data = request.get_json(force=True) if request.is_json else request.form.to_dict()
        ticker = (data.get("ticker") or "").strip().upper()
        trade_date = (data.get("trade_date") or "").strip()

        if not ticker:
            return jsonify({"error": "Champ requis manquant: ticker"}), 400
        if not trade_date:
            return jsonify({"error": "Champ requis manquant: trade_date"}), 400

        # Optional custom config
        user_cfg = data.get("config") or {}

        # Optional quick mode to reduce workload and external calls
        quick = str(data.get("quick", "false")).lower() in {"1", "true", "yes", "on"}
        if quick:
            user_cfg = {
                **user_cfg,
                "max_debate_rounds": 1,
                "max_risk_discuss_rounds": 1,
                "online_tools": True,  # allow minimal online tools
            }
            # Keep analysts minimal for speed
            selected_analysts = ["market", "news"]
        else:
            selected_analysts = user_cfg.get("selected_analysts", ["market", "social", "news", "fundamentals"])
        cfg = build_config(user_cfg)

        if cfg.get("__no_provider__"):
            return (
                jsonify(
                    {
                        "error": "Aucune clé API détectée. Configurez GROQ_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY ou GOOGLE_API_KEY.",
                        "hint": "export GROQ_API_KEY=... (recommandé) ou OPENAI_API_KEY=...",
                    }
                ),
                400,
            )

        graph = TradingAgentsGraph(selected_analysts=selected_analysts, debug=False, config=cfg)

        final_state, decision = graph.propagate(ticker, trade_date)

        # Keep response lightweight, include core sections
        response = {
            "ticker": ticker,
            "trade_date": trade_date,
            "decision": decision,
            "summaries": {
                "market": final_state.get("market_report"),
                "sentiment": final_state.get("sentiment_report"),
                "news": final_state.get("news_report"),
                "fundamentals": final_state.get("fundamentals_report"),
            },
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def create_app() -> Flask:
    return app


@app.errorhandler(Exception)
def _handle_exception(e):
    # Ensure JSON error for API calls; fall back to text for others
    try:
        path = request.path
        if path.startswith("/api/"):
            return jsonify({"error": str(e)}), 500
    except Exception:
        pass
    return (str(e), 500, {"Content-Type": "text/plain; charset=utf-8"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5050"))
    app.run(host="0.0.0.0", port=port, debug=True)
