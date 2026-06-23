# Recall Agent 🧠

An AI-powered spaced repetition learning assistant built in Python. Recall Agent helps you retain concepts over time by leveraging the **SuperMemo-2 (SM-2) algorithm** to schedule reviews, notifying you via **Discord Webhooks** when concepts are due, and grading your typed responses using the **Google Gemini API**.

---

## 🛠️ Tech Stack & Features

*   **Python 3.11+**: Modular, readable, and clean implementation.
*   **SuperMemo-2 (SM-2)**: Core scheduling logic to dynamically calculate the next optimal review interval based on grading quality.
*   **Google Gemini API (`gemini-3.5-flash`)**: Leverages the new `google-genai` SDK with **Structured Outputs** to score answers from 0 to 5 and provide constructive feedback.
*   **Discord Webhooks**: Sends notifications/questions directly to a configured Discord channel when a review session begins.
*   **Simulation Mode**: Allows offline and keyless demonstration to test the workflow without configuring Discord webhooks or Gemini API keys.
*   **Local JSON Memory Storage**: Persists all concepts and history in `memory.json`.

---

## 📁 File Structure

*   [`memory.py`](file:///c:/Users/patel/Downloads/cap/memory.py): Handles database loading, saving, concept addition, and filtering due items.
*   [`scheduler.py`](file:///c:/Users/patel/Downloads/cap/scheduler.py): Implements the mathematical formula for the SM-2 algorithm.
*   [`messenger.py`](file:///c:/Users/patel/Downloads/cap/messenger.py): Dispatches messages and questions to a Discord channel.
*   [`grader.py`](file:///c:/Users/patel/Downloads/cap/grader.py): Interfaces with Gemini API using structured response validation.
*   [`main.py`](file:///c:/Users/patel/Downloads/cap/main.py): CLI interface to run reviews, add concepts, list memory, or run simulations.
*   [`requirements.txt`](file:///c:/Users/patel/Downloads/cap/requirements.txt): Lists all third-party package dependencies.
*   [`.env.example`](file:///c:/Users/patel/Downloads/cap/.env.example): Template for setting environment credentials.

---

## 🚀 Setup Instructions

1.  **Clone / Copy** this project directory.
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Setup Environment Variables**:
    Create a `.env` file based on `.env.example`:
    ```bash
    cp .env.example .env
    ```
    Populate the variables:
    *   `GEMINI_API_KEY`: Get one from [Google AI Studio](https://aistudio.google.com/).
    *   `DISCORD_WEBHOOK_URL`: (Optional for simulation/local-only, required for Discord integration) Create a webhook in your Discord channel's integration settings.

---

## ⚙️ How it Works: SM-2 Spaced Repetition

The **SuperMemo-2 (SM-2)** algorithm schedules the next review for each concept based on the grade quality $q$ (scored from 0 to 5):
*   **5**: Perfect response.
*   **4**: Correct response after hesitation or minor omissions.
*   **3**: Correct response, but with significant omissions/difficulties.
*   **2**: Incorrect response, but easy to recall (partially correct).
*   **1**: Incorrect response, but user remembered the concept name.
*   **0**: Complete blackout/wrong.

### Algorithm Calculations:
1.  **If response is correct ($q \ge 3$):**
    *   For the 1st repetition: $I(1) = 1$ day.
    *   For the 2nd repetition: $I(2) = 6$ days.
    *   For subsequent repetitions: $I(n) = I(n-1) \times EF$ (rounded to the nearest integer).
    *   Increment repetitions count by 1.
2.  **If response is incorrect ($q < 3$):**
    *   Reset repetitions to 0.
    *   Reset interval to 1 day.
3.  **Adjust the Easiness Factor ($EF$):**
    *   $EF' = EF + (0.1 - (5 - q) \times (0.08 + (5 - q) \times 0.02))$
    *   If $EF' < 1.3$, set $EF' = 1.3$ (minimum floor limit).

---

## 🖥️ Usage

Run the main application:
```bash
python main.py
```

### Menu Options
1.  **Review Due Concepts**: Pulls all concepts whose next review date is today or earlier. Posts them to Discord, takes your input in the CLI, grades via Gemini, and saves the updated schedules.
2.  **Add a Concept**: Lets you add a new concept, a prompt question, and the expected answer.
3.  **List All Concepts**: View a summary table of all stored concepts, review intervals, repetitions, and next scheduled review date.
4.  **Run Simulation Mode**: Simulates adding concepts, sending a mock Discord message, prompting for mock answers, and mock-grading them without needing active keys.
5.  **Exit**
