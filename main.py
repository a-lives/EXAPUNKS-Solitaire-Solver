from bot import Board, Order, Card
from gui import GameWindow, WINDOW_TITLE, SUIT_MAP

import time
import pyautogui


if __name__ == "__main__":
    window = GameWindow.find_by_title(WINDOW_TITLE)
    window.activate()
    time.sleep(3)

    while 1:
        window.activate()
        time.sleep(2)
        window.start_game()
        board = window.new_board()
        print(board)
        """ while not board.valid():
            text = input(">>>")
            if text == "done":
                break
            try:
                x,y,order_s = text.split(" ")
                x,y = int(x),int(y)
                order = Order(int(order_s))
                o_suit = board.grid[(x,y)].suit
                card = Card(o_suit,order)
                board.grid[(x,y)] = card
                print(board)
            except:
                try:
                    x,y,suit_s,order_s = text.split(" ")
                    x,y = int(x),int(y)
                    if suit_s not in ["black","red"]:
                        order = Order.HUMAN
                    else:
                        order = Order(int(order_s))
                    card = Card(SUIT_MAP[suit_s],order)
                    board.grid[(x,y)] = card
                    print(board)
                except:
                    print("Error") """

        if not board.valid():
            print("\aDetect fail")
            continue
        pyautogui.move(-100, -100)
        moves = board.solve()
        if moves:
            window.activate()
            time.sleep(2)
            window.send_moves(moves, show=True, board=board)
            print("We hope it done...")
            time.sleep(2)
