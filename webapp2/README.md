webapp2 - Minimal Flask interface for TradingAgents

Quick start
- Ensure dependencies from project root are installed; then install webapp2 extras (Flask only).
- Set one provider API key (recommended: GROQ_API_KEY) or OPENAI_API_KEY / ANTHROPIC_API_KEY / GOOGLE_API_KEY.

Env examples
export GROQ_API_KEY=your_key_here
# or
export OPENAI_API_KEY=your_openai_key

Run
python webapp2/app.py

Then open http://localhost:5050 and run an analysis.

Notes
- This app creates a TradingAgentsGraph and calls propagate(ticker, trade_date).
- It mirrors GROQ_API_KEY into OPENAI_API_KEY for OpenAI-compatible clients.
- Keep trade_date in YYYY-MM-DD format.
