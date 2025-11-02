import os
import sys

from dotenv import load_dotenv; load_dotenv()
# Support running as a module (python -m backend.app.booking_cli)
# and as a script (python backend/app/booking_cli.py)
from app.agents.booking_model import complete_booking_turn  # type: ignore



def main():
    print("MedCare Booking (terminal). Type 'exit' to quit.")
    history = []
    while True:
        try:
            user = input("> ").strip()
            if user.lower() in {"exit", "quit"}:
                print("Goodbye!")
                break
            resp = complete_booking_turn(history, user)
            print(resp["content"])
            history.append({"role": "user", "content": user})
            history.append(resp)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    # Ensure CAL_API_BASE points at your running API if not default
    os.environ.setdefault("CAL_API_BASE", "http://localhost:8000")
    main()
