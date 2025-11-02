#!/usr/bin/env python3
"""Interactive test script for the booking model - can run directly without web server"""
import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.booking_model import complete_booking_turn


def interactive_booking_chat():
    """Interactive booking chat with the model"""

    print("=" * 60)
    print("🏥 MedCare Clinic - Booking Assistant")
    print("=" * 60)
    print("Type 'exit' to end the conversation")
    print("=" * 60)

    # Simulate conversation history (empty for first message)
    history = []

    while True:
        try:
            # Get user input
            user_input = input("\n📤 You: ").strip()

            # Check for exit command
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n📥 Sarah: Thanks for calling MedCare Clinic! Have a great day!")
                print("=" * 60)
                print("✅ Chat ended. Goodbye!")
                print("=" * 60)
                break

            # Skip empty inputs
            if not user_input:
                print("📥 Sarah: I didn't catch that. Could you repeat that?")
                continue

            # Get assistant response
            assistant_response = complete_booking_turn(history, user_input)
            print(f"📥 Sarah: {assistant_response['content']}")

            # Add to history
            history.append({"role": "user", "content": user_input})
            history.append(assistant_response)

        except KeyboardInterrupt:
            print("\n\n📥 Sarah: Thanks for calling MedCare Clinic! Have a great day!")
            print("=" * 60)
            print("✅ Chat ended. Goodbye!")
            print("=" * 60)
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("📥 Sarah: Sorry, I'm having some technical difficulties. Could you try again?")


if __name__ == "__main__":
    try:
        interactive_booking_chat()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
