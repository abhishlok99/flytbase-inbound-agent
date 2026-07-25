# FlytBase Inbound BDR Agent

7-stage inbound lead qualification/research/routing pipeline built for the FlytBase BDR Hiring Hackathon (Inbound track).

## Quickstart
```
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```
Visit `http://localhost:8000/`.

## Optional: enable live LLM drafting for Stage 3
Set ONE of these env vars before starting the app — without any set, Stage 3 runs in structured-template mode (still real, non-generic logic, just not free-form generative prose):
```
export ANTHROPIC_API_KEY=...   # or
export OPENAI_API_KEY=...      # or
export GOOGLE_API_KEY=...      # Gemini, has a free tier
export GROQ_API_KEY=...        # Llama on Groq, free tier, fast
```

## Deploying (fastest path: Render or Railway)
1. Push this folder to a new GitHub repo.
2. Render: New → Web Service → connect the repo → Build command `pip install -r requirements.txt` → Start command `uvicorn app:app --host 0.0.0.0 --port $PORT`.
   Railway: New Project → Deploy from GitHub → it auto-detects Python; set the same start command if prompted.
3. Set any LLM env var (optional) in the platform's environment settings.
4. Confirm the deployed URL loads `/` and `/health` before submitting.

## Structure
```
fetchers/       real, keyless data sources (SEC EDGAR, Google News RSS, flytbase.com)
stages/         the 7 pipeline stages, each independently testable
llm_adapter.py  pluggable LLM backend for Stage 3 (falls back to template mode)
orchestrator.py wires all stages together
app.py          FastAPI app -- the live deployed link
mindmap.html    self-contained thought-process diagram (submission deliverable)
Submission.md   submission writeup (regenerate via the platform's prompt before final submit)
```
