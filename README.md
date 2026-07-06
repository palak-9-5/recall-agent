# Recall Agent – AI-Powered Spaced Repetition Learning Agent

## The Problem
Spaced repetition is proven to boost long‑term retention, but users often forget to open the app at the right time. Recall Agent proactively reaches into your daily workflow, reminding you when reviews are due instead of waiting for you to remember.

## How It Works
- **SM‑2 algorithm** – Calculates optimal review intervals based on grading quality.
- **Google Gemini API** – AI‑grades your answers (0‑5) and provides constructive feedback.
- **Discord webhook** – Sends proactive notifications to a Discord channel when a concept is due.
- **memory.json** – Persists concepts, scheduling data, and review history across sessions.

## Features
- Add new concepts with custom questions.
- AI‑graded reviews using Gemini.
- Forgetting‑curve‑driven scheduling (SM‑2).
- Discord alerts for upcoming reviews.
- Analytics dashboard (Streamlit) showing total concepts, due today, review stats.
- CLI utilities + Streamlit UI for interaction.

## Tech Stack
- **Python**
- **Streamlit** (web UI)
- **Google Gemini API** (AI grading)
- **Discord Webhooks** (notifications)
- **SM‑2 Algorithm** (spaced repetition)

## Setup & Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/recall-agent.git
   cd recall-agent
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the required keys (see below).
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Environment Variables
| Variable               | Description                                 | Where to obtain |
|------------------------|---------------------------------------------|-----------------|
| `GEMINI_API_KEY`       | API key for Google Gemini                  | Google AI Studio |
| `DISCORD_WEBHOOK_URL` | Discord webhook URL for notifications      | Your Discord server (Create a webhook in channel settings) |

## Project Structure
```
recall-agent/
├── app.py            # Streamlit UI entry point
├── main.py           # Core routing & page logic
├── memory.py         # JSON persistence utilities
├── scheduler.py      # SM‑2 scheduling implementation
├── grader.py         # Gemini API wrapper for grading
├── messenger.py      # Discord webhook helper
├── memory.json       # Persistent data store (generated at runtime)
└── assets/
    └── logo.png     # Project logo
```

## Built For
Capstone project submission for the **Kaggle 5‑Day AI Agents Intensive Course** with Google.

## License
MIT License
