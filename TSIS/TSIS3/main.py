from racer import run_game
from ui import main_menu

# просто точка входа
if __name__ == "__main__":
    while True:
        action = main_menu()

        if action == "play":
            run_game()
        elif action == "quit":
            break