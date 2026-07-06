import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import our custom modules
import memory
import scheduler
import messenger
import grader

# Load environment variables from a .env file (if present)
load_dotenv()

MEMORY_FILE = "memory.json"
SIMULATION_MEMORY_FILE = "simulation_memory.json"


def clear_screen():
    # Simple cross-platform screen clear helper
    os.system("cls" if os.name == "nt" else "clear")


def print_header(title: str):
    print("=" * 60)
    print(f" {title:^58} ")
    print("=" * 60)


def handle_add_concept(filepath: str = MEMORY_FILE):
    print_header("Add New Concept")

    concept_name = input(
        "Enter the concept name (e.g., 'Python decorators'): "
    ).strip()
    if not concept_name:
        print("Error: Concept name cannot be empty.")
        return

    question = input("Enter the review question/prompt: ").strip()
    if not question:
        print("Error: Question cannot be empty.")
        return

    expected_answer = input(
        "Enter expected answer / key points to grade against: "
    ).strip()
    if not expected_answer:
        print("Error: Expected answer cannot be empty.")
        return

    # Add to database
    try:
        memory.add_concept(concept_name, question, expected_answer, filepath)
        print(
            f"\nSuccess! Concept '{concept_name}' added to memory and scheduled for review today!"
        )
    except ValueError as e:
        print(f"\nError: {e}")


def handle_list_concepts(filepath: str = MEMORY_FILE):
    print_header("All Stored Concepts")

    db = memory.load_memory(filepath)
    if not db:
        print("No concepts stored in memory yet.")
        return

    # Print a clean, formatted table
    print(
        f"{'Concept Name':<22} | {'EF':<5} | {'Interval':<8} | {'Reps':<5} | {'Next Review':<11}"
    )
    print("-" * 60)
    for name, details in db.items():
        print(
            f"{name[:22]:<22} | "
            f"{details.get('easiness', 2.5):<5.2f} | "
            f"{details.get('interval', 0):<8} | "
            f"{details.get('repetitions', 0):<5} | "
            f"{details.get('next_review', ''):<11}"
        )
    print("-" * 60)
    print(f"Total concepts: {len(db)}")


def handle_review_session(
    filepath: str = MEMORY_FILE, is_simulation: bool = False
):
    print_header("Active Review Session")

    db = memory.load_memory(filepath)
    due_concepts = memory.get_due_concepts(db)

    if not due_concepts:
        print(
            "🎉 Hurrah! No reviews due at this moment. You are all caught up!"
        )
        return

    print(f"You have {len(due_concepts)} review(s) due today.\n")

    # Grab environment variables
    discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
    gemini_key = os.getenv("GEMINI_API_KEY")

    for i, (name, details) in enumerate(due_concepts.items(), 1):
        print(f"--- Review {i} of {len(due_concepts)}: {name} ---")

        question = details["question"]
        expected = details["expected_answer"]

        # 1. Notify/Send via Discord Webhook
        discord_message = f"🧠 **Recall Agent Review Time!**\n**Concept:** {name}\n**Question:** {question}"
        if is_simulation:
            print(
                f"[MOCK DISCORD WEBHOOK] Sending message:\n{discord_message}"
            )
        else:
            messenger.send_to_discord(discord_webhook, discord_message)

        # 2. Present Question to User in CLI
        print(f"\nQuestion: {question}")
        user_response = input("Your Answer: ").strip()

        if not user_response:
            print("Blank answer submitted. Grading as blackout (0).")
            user_response = "[No response entered]"

        # 3. Grade the answer using Gemini API (or Mock if Simulation)
        print("\nGrading your response...")

        score = 0
        feedback = ""

        if is_simulation:
            # Smart Mock Grader: Counts overlapping keywords for a basic score
            expected_words = set(expected.lower().split())
            user_words = set(user_response.lower().split())
            overlap = len(expected_words.intersection(user_words))

            # Formulate a basic mock grade based on matching keywords
            if overlap >= 3 or (
                len(expected_words) > 0
                and (overlap / len(expected_words)) >= 0.5
            ):
                score = 5
                feedback = "[MOCK FEEDBACK] Outstanding! Your answer covers almost all the core key points of the expected details. Good job."
            elif overlap >= 1:
                score = 3
                feedback = "[MOCK FEEDBACK] Correct in spirit, but you missed some of the expected key details. Read the expected answer to fill the gap."
            else:
                score = 1
                feedback = "[MOCK FEEDBACK] Incorrect answer. It didn't seem to contain the correct expected terms. Take a look at the expected answer details."
        else:
            try:
                score, feedback = grader.grade_answer(
                    question, expected, user_response, gemini_key
                )
            except Exception as e:
                print(f"\n❌ Grading Error: {e}")
                print("Falling back to manual scoring.")
                while True:
                    try:
                        score = int(
                            input(
                                "Please enter a manual score (0 = forgot, 5 = perfect): "
                            )
                        )
                        if 0 <= score <= 5:
                            feedback = "Manually graded by user."
                            break
                        print("Score must be between 0 and 5.")
                    except ValueError:
                        print("Invalid integer. Try again.")

        # 4. Show User Results
        print(f"Grade: {score}/5")
        print(f"Feedback: {feedback}")
        print(f"Expected Answer was: {expected}\n")

        # 5. Calculate SM-2 Updates
        curr_easiness = details.get("easiness", 2.5)
        curr_interval = details.get("interval", 0)
        curr_reps = details.get("repetitions", 0)

        new_interval, new_easiness, new_reps = scheduler.calculate_next_review(
            score, curr_easiness, curr_reps, curr_interval
        )

        # Calculate the next review calendar date
        today_date = datetime.now()
        next_review_date = today_date + timedelta(days=new_interval)
        next_review_str = next_review_date.strftime("%Y-%m-%d")

        # 6. Save History and Update Concept
        review_entry = {
            "date": today_date.strftime("%Y-%m-%d %H:%M:%S"),
            "user_answer": user_response,
            "grade_quality": score,
            "feedback": feedback,
        }

        db[name]["easiness"] = new_easiness
        db[name]["interval"] = new_interval
        db[name]["repetitions"] = new_reps
        db[name]["next_review"] = next_review_str
        db[name].setdefault("history", []).append(review_entry)

        # Save memory intermediate to disk so progress isn't lost if aborted
        memory.save_memory(db, filepath)

        print(
            f"Concept scheduled. Next review in {new_interval} day(s) ({next_review_str}).\n"
        )

    print("Session complete! Memory database successfully updated.")


def run_simulation_mode():
    print_header("Starting Simulation Mode")
    print(
        "This mode simulates the spaced repetition process using a temporary database."
    )
    print(
        "You do NOT need active Gemini API keys or Discord webhooks for this mode.\n"
    )

    # Initialize the simulation memory file with sample concepts if it doesn't exist
    if not os.path.exists(SIMULATION_MEMORY_FILE):
        print("Seeding simulation database with sample concepts...")
        memory.add_concept(
            "Python decorators",
            "What is a decorator in Python, and how is it defined?",
            "A decorator is a function that takes another function as an argument, extends its behavior without modifying it, and returns a new function. It is defined using the @ symbol syntax.",
            SIMULATION_MEMORY_FILE,
        )
        memory.add_concept(
            "REST API HTTP Methods",
            "Name the 4 primary HTTP methods used in REST APIs and their typical CRUD mapping.",
            "GET maps to Read, POST maps to Create, PUT maps to Update/Replace, and DELETE maps to Delete.",
            SIMULATION_MEMORY_FILE,
        )

    input("Press Enter to begin the simulated review session...")
    clear_screen()

    handle_review_session(SIMULATION_MEMORY_FILE, is_simulation=True)

    print("\nSimulation database contents after review:")
    handle_list_concepts(SIMULATION_MEMORY_FILE)

    input("\nPress Enter to return to main menu...")


def handle_statistics(filepath: str = MEMORY_FILE):
    print_header("Learning Statistics Dashboard")

    db = memory.load_memory(filepath)
    if not db:
        print("+" + "-" * 58 + "+")
        print(f"| {'No data yet. Add some concepts to start learning!':^56} |")
        print("+" + "-" * 58 + "+")
        return

    total_concepts = len(db)
    today_str = datetime.now().strftime("%Y-%m-%d")
    concepts_due_today = sum(
        1 for details in db.values() if details.get("next_review") == today_str
    )
    total_reviews = sum(
        len(details.get("history", [])) for details in db.values()
    )
    avg_easiness = round(
        sum(details.get("easiness", 2.5) for details in db.values())
        / total_concepts,
        2,
    )

    correct_reviews = sum(
        1
        for details in db.values()
        for h in details.get("history", [])
        if h.get("grade_quality", 0) >= 3
    )
    incorrect_reviews = sum(
        1
        for details in db.values()
        for h in details.get("history", [])
        if h.get("grade_quality", 0) < 3
    )

    most_difficult = min(
        db.items(), key=lambda item: item[1].get("easiness", 2.5)
    )[0]
    strongest = max(db.items(), key=lambda item: item[1].get("easiness", 2.5))[
        0
    ]

    print("+" + "-" * 58 + "+")
    print(f"| {'METRIC':<35} | {'VALUE':<18} |")
    print("+" + "-" * 58 + "+")
    print(f"| {'Total Concepts':<35} | {total_concepts:<18} |")
    print(f"| {'Concepts Due Today':<35} | {concepts_due_today:<18} |")
    print(f"| {'Total Reviews Completed':<35} | {total_reviews:<18} |")
    print(f"| {'Average Easiness Factor':<35} | {avg_easiness:<18.2f} |")
    print(f"| {'Correct Reviews (Grade >= 3)':<35} | {correct_reviews:<18} |")
    print(
        f"| {'Incorrect Reviews (Grade < 3)':<35} | {incorrect_reviews:<18} |"
    )

    # Truncate concept names if they are too long to fit in the value column
    truncated_difficult = most_difficult[:18]
    truncated_strongest = strongest[:18]
    print(f"| {'Most Difficult Concept':<35} | {truncated_difficult:<18} |")
    print(f"| {'Strongest Concept':<35} | {truncated_strongest:<18} |")
    print("+" + "-" * 58 + "+")


def main():
    while True:
        clear_screen()
        print_header("RECALL AGENT: AI Spaced Repetition Assistant")
        print("1. Review Due Concepts (Active Mode)")
        print("2. Add a Concept")
        print("3. List All Concepts")
        print("4. Run Simulation Mode")
        print("5. View Learning Statistics")
        print("6. Exit")
        print("=" * 60)

        choice = input("Enter choice (1-6): ").strip()

        if choice == "1":
            clear_screen()
            handle_review_session(MEMORY_FILE, is_simulation=False)
            input("\nPress Enter to return to main menu...")
        elif choice == "2":
            clear_screen()
            handle_add_concept(MEMORY_FILE)
            input("\nPress Enter to return to main menu...")
        elif choice == "3":
            clear_screen()
            handle_list_concepts(MEMORY_FILE)
            input("\nPress Enter to return to main menu...")
        elif choice == "4":
            clear_screen()
            run_simulation_mode()
        elif choice == "5":
            clear_screen()
            handle_statistics(MEMORY_FILE)
            input("\nPress Enter to return to main menu...")
        elif choice == "6":
            print("\nKeep learning! Goodbye.")
            break
        else:
            input("\nInvalid option. Press Enter to try again...")


if __name__ == "__main__":
    main()
