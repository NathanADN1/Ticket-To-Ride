from time import time, sleep
from game import Game
from game.classes import FailureCause
import tkinter as tk
from tkinter import Label, Button

class Driver:

    def __init__(self, players, use_gui=True, print_debug=True, exception_on_bad_action=True, pause_between_turns=0,
                 maximum_rounds=1000):
        self.players = players
        self.use_gui = use_gui
        self.print_debug = print_debug
        self.exception_on_bad_action = exception_on_bad_action
        self.pause_between_turns = pause_between_turns
        self.maximum_rounds = maximum_rounds
        self.game_gui = None
        self.winner = None
        self.game = None
        self.game_start_time = 0

        # Enable or Turn off player's debug
        for player in self.players:
            player.print_debug = print_debug

    def run_game(self):
        self.game = self.create_game()
        self.play_game(self.game)

    def create_game(self):
        return Game(self.players, self.maximum_rounds, self.print_debug)

    def play_game(self, game):
        self.game_start_time = time()

        if self.use_gui:
            from gui import gui
            self.game_gui = gui.GUI()
            game.gui = self.game_gui  # I thought this would not be too terrible

        # Main game loop.  Tells players when to take their turn.
        while not game.is_game_over()[0]:
            for player in self.players:
                if game.is_turn(player):
                    action_to_perform = player.take_turn(game)

                    player_info = game.get_player_info(player)
                    if self.use_gui:
                        self.game_gui.update(game)

                    # Perform action.
                    action_result = game.perform_action(player, action_to_perform)

                    player.on_action_complete(game, action_result)

                    # Print results.  This happens after the action is performed so the timing is correct when drawing
                    # destinations.
                    if self.print_debug:
                        game.print_face_up_cards()
                        print("Player %s: %s\nDoing Action: %s" % (player.name, player_info, action_to_perform))

                        debug_print = player.debug_print(game)

                        if debug_print != "":
                            print(debug_print)

                        print("")

                    # If the action fails, raise an exception indicating what went wrong.
                    if not action_result[0] and self.exception_on_bad_action:
                        raise Exception("Failure", FailureCause.str(action_result[1]))

                    if self.pause_between_turns > 0:
                        sleep(self.pause_between_turns)

                    break

        self.game_over(game)
        if self.use_gui:
            self.game_gui.close()

    def game_over(self, game):
        # Game's over.  Tell the players and print out some results.
        for player in self.players:
            player.game_ended(game)
        self.winner = game.is_game_over()[1]
        execution_time = time() - self.game_start_time
        final_scores = game.get_visible_scores()


        # Show game over window
        if self.use_gui:
            self.show_game_over_window(execution_time,self.winner, final_scores)

        print("Execution Time: %.2f seconds" % (time() - self.game_start_time))
        print("Game Over")
        print("Winner: %s" % self.winner)
        print("Final Scores: %s" % game.get_visible_scores())
        print("")

        if self.use_gui:
            self.game_gui.update_game_ended(game)

    def show_game_over_window(self, execution_time, winner, final_scores):
        root = tk.Tk()
        # Get screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Set the window size to the screen size
        root.geometry(f"{screen_width}x{screen_height}")

        root.title("Game Over")

        root.configure(bg="#f0f0f0")

        Label(root, text="Execution Time: %.2f seconds" % execution_time, font=("Arial", 44), bg="#f0f0f0").pack(pady=10)
        Label(root, text="Game Over", font=("Arial", 48, "bold"), bg="#f0f0f0").pack(pady=10)
        Label(root, text="Winner: %s" % winner, font=("Arial", 44), bg="#f0f0f0").pack(pady=10)
        Label(root, text="Final Scores: %s" % final_scores, font=("Arial", 44), bg="#f0f0f0").pack(pady=10)
        Label(root, text="To Play again, press Close and select a new ticket to discard", font=("Arial", 44), bg="#f0f0f0").pack(pady=10)


        Button(root, text="Close", command=root.destroy, font=("Arial", 64), bg="#f44336", fg="white").pack(pady=20)

        return root

    def get_winner(self):
        """
        get winner of the game
        :return:
        """
        return self.winner
    
    
