# Information Ecosystem Guessing Game (MVP)

A minimal Streamlit prototype for a 5-clue guessing game about actors in the information ecosystem.

## Quick Start

1. Create a virtual environment (optional but recommended). Example (on macOS/Linux):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
   On Windows (PowerShell):
   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   streamlit run app.py
   ```

4. Optional query parameters for quick A/B tests:
   - `?reliability=true` → Shows reliability labels on clues (Low/Med/High).
   - `?rationale=true` → Shows a short rationale for why a clue is discriminative.

   Example:
   ```
   http://localhost:8501/?reliability=true&rationale=true
   ```

## Files
- `app.py` — Streamlit app.
- `data/actors.json` — Content pack with sample actors and clues.
- `logs/pilot_log.csv` — Gameplay logs (created at runtime).

## Notes
- Only *class/type* is guessed (e.g., Bot Ağı, Trol Çiftliği, vb.).
- Each round has up to 5 clues. Early correct guesses score more.
- The dataset is intentionally small for pilot; extend `actors.json` to add more actors.