# Recall Agent – AI-Powered Spaced Repetition Learning Agent

## The Problem
Spaced repetition works, but people forget to open the app. This agent reaches into your life, sending proactive reminders instead of waiting for you.

## How It Works
- **SM‑2 algorithm** – Calculates optimal review intervals based on grading quality.
- **Gemini API** – AI grades your answers (0‑5) and provides feedback.
- **Discord webhook** – Sends proactive notifications when reviews are due.
- **`memory.json`** – Persists concepts, schedules, and review history.

## Features
- Add concepts
- AI‑graded reviews
- Forgetting‑curve scheduling
- Discord alerts
- Analytics dashboard
- CLI + Streamlit UI

## Tech Stack
- Python
- Streamlit
- Google Gemini API
- Discord Webhooks
- SM‑2 Algorithm

## Setup & Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/recall-agent.git
cd recall-agent

# Install dependencies
pip install -r requirements.txt

# Create a .env file
# Replace the placeholders with your actual keys
cat <<EOF > .env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
DISCORD_WEBHOOK_URL=YOUR_DISCORD_WEBHOOK_URL
EOF

# Run the app
streamlit run app.py
```

## Environment Variables
| Variable            | Description                         | Where to obtain                                 |
|---------------------|-------------------------------------|------------------------------------------------|
| `GEMINI_API_KEY`    | Gemini API key for AI grading       | Google Cloud Console (GenAI API)               |
| `DISCORD_WEBHOOK_URL`| Discord webhook for notifications   | Discord server → Integrations → Webhooks        |

## Project Structure
```
recall-agent/
├─ app.py          # Streamlit UI entry point
├─ main.py         # CLI routing & page logic
├─ memory.py       # JSON persistence utilities
├─ scheduler.py    # SM‑2 scheduling implementation
├─ grader.py       # Gemini API wrapper for grading
├─ messenger.py    # Discord webhook helper
├─ notifier.py     # Daily Discord notification script
├─ memory.json     # Persistent data store (generated at runtime)
└─ assets/
   └─ logo.png     # Project logo
```

## Built For
Capstone project submission for the **Kaggle 5‑Day AI Agents Intensive Course** with Google.

## License
MIT
