import typing as t
import bot
from bot import Suit, Order
import pyautogui
import time
import cv2
import win32gui
import win32con
import PIL.Image, PIL.ImageGrab, PIL.ImageDraw
import numpy as np
import os
from paddleocr import PaddleOCR

import locale


def getpreferredencoding(do_setlocale=True):
    return "utf-8"


locale.getpreferredencoding = getpreferredencoding

import logging

logging.disable(logging.DEBUG)  # 关闭DEBUG日志的打印
logging.disable(logging.WARNING)  # 关

ocr = PaddleOCR(debug=False, use_angle_cls=False, lang="en")

BBox: t.TypeAlias = t.Tuple[int, int, int, int]  # left, top, right, bottom
Image: t.TypeAlias = PIL.Image.Image

WINDOW_TITLE = "EXAPUNKS"
IMAGEGRAB_PARAMS = {"xdisplay": None}
LEFTTOP = (491, 696)
RIGHTTOP = (1844, 393)
OFFSET_X = 178
OFFSET_Y = 40
TILE_SIZE = (40, 25)
START = (1827, 1277)
SCREEN_SIZE = (2560, 1600)

SUIT_MAP = {
    "black": Suit.SPADE,
    "red": Suit.HEART,
    "club": Suit.CLUB,
    "diamond": Suit.DIAMOND,
    "spade": Suit.SPADE,
    "heart": Suit.HEART,
}


class GameWindow:
    def __init__(self, window: int):
        self.window: int = window

    def __str__(self) -> str:
        return win32gui.GetWindowText(self.window)

    @classmethod
    def find_by_title(cls, title: str) -> "GameWindow":
        windows = win32gui.FindWindow(None, WINDOW_TITLE)
        window = cls(windows)
        return window

    @property
    def bbox(self) -> BBox:
        return win32gui.GetWindowRect(self.window)

    @property
    def isActivate(self) -> bool:
        return win32gui.GetForegroundWindow() == self.window

    def activate(self) -> bool:
        if win32gui.IsWindow(self.window):
            win32gui.SetForegroundWindow(self.window)
        else:
            print("Window not found")

    def take_screenshot(self) -> Image:
        bbox: BBox = self.bbox
        image = PIL.ImageGrab.grab(bbox, **IMAGEGRAB_PARAMS)  # RGBA in macOS
        if image.mode != "RGB":
            image = image.convert(mode="RGB")
        return image

    def close(self) -> None:
        win32gui.PostMessage(self.window, win32con.WM_CLOSE, 0, 0)

    def new_board(self, debug: bool = False) -> bot.Board:
        image: Image = self.take_screenshot()
        board = bot.Board()
        results = self.prase_image(image)
        for x in range(9):
            for y in range(4):
                board.grid[(x + 1, y + 1)] = results[x * 4 + y]
        return board

    def new_board_from_local(self, path: str) -> bot.Board:
        image: Image = PIL.Image.open(path)
        board = bot.Board()
        results = self.prase_image(image)
        for y in range(4):
            for x in range(9):
                board.grid[(x + 1, y + 1)] = results[x * 4 + y]
        return board

    def start_game(self) -> None:
        pyautogui.moveTo(START[0], START[1])
        pyautogui.mouseDown()
        pyautogui.mouseUp()
        time.sleep(8)

    def send_moves(
        self, moves: t.List[bot.Move], show: bool = False, board: bot.Board = None
    ) -> None:
        if show:
            assert board is not None
            board = board.clone()
        for move in moves:
            if self.isActivate:
                ori_pos = (
                    (
                        LEFTTOP[0] + OFFSET_X * (move.start[0] - 1) + 10,
                        LEFTTOP[1] + OFFSET_Y * (move.start[1] - 1) + 10,
                    )
                    if move.start[0] > 0
                    else RIGHTTOP
                )
                tar_pos = (
                    (
                        LEFTTOP[0] + OFFSET_X * (move.end[0] - 1) + 10,
                        LEFTTOP[1] + OFFSET_Y * (move.end[1] - 1) + 10,
                    )
                    if move.end[0] > 0
                    else RIGHTTOP
                )
                pyautogui.moveTo(ori_pos[0], ori_pos[1])
                pyautogui.mouseDown()
                pyautogui.moveTo(tar_pos[0], tar_pos[1])
                pyautogui.mouseUp()
                if show:
                    board.move(move)
                    os.system("cls")
                    print(board)
                # time.sleep(0.1)
            else:
                input()
                self.activate()
                time.sleep(3)
                ori_pos = (
                    (
                        LEFTTOP[0] + OFFSET_X * (move.start[0] - 1) + 10,
                        LEFTTOP[1] + OFFSET_Y * (move.start[1] - 1) + 10,
                    )
                    if move.start[0] > 0
                    else RIGHTTOP
                )
                tar_pos = (
                    (
                        LEFTTOP[0] + OFFSET_X * (move.end[0] - 1) + 10,
                        LEFTTOP[1] + OFFSET_Y * (move.end[1] - 1) + 10,
                    )
                    if move.end[0] > 0
                    else RIGHTTOP
                )
                pyautogui.moveTo(ori_pos[0], ori_pos[1])
                pyautogui.mouseDown()
                pyautogui.moveTo(tar_pos[0], tar_pos[1])
                pyautogui.mouseUp()
                if show:
                    board.move(move)
                    os.system("cls")
                    print(board)
                # time.sleep(0.1)

    def prase_image(self, image: Image) -> t.List[str]:
        # size = image.size
        array = np.array(image)  # (h,w,c)
        results = []
        for x in range(0, 9):
            for y in range(0, 4):
                tile = array[
                    LEFTTOP[1]
                    + OFFSET_Y * y : LEFTTOP[1]
                    + OFFSET_Y * y
                    + TILE_SIZE[1],
                    LEFTTOP[0]
                    + OFFSET_X * x : LEFTTOP[0]
                    + OFFSET_X * x
                    + TILE_SIZE[0],
                    :,
                ]
                ex_tile = array[
                    LEFTTOP[1]
                    + OFFSET_Y * y : LEFTTOP[1]
                    + OFFSET_Y * y
                    + TILE_SIZE[1],
                    LEFTTOP[0]
                    + OFFSET_X * x
                    - 7 : LEFTTOP[0]
                    + OFFSET_X * x
                    + TILE_SIZE[0]
                    + 7,
                    :,
                ]
                target = None
                max_score = 0
                paths = os.listdir("./templates")
                for path in paths:
                    score = 0
                    num_tpl = 0
                    for match_tiles in os.listdir("./templates/" + path):
                        num_tpl += 1
                        tt = self.load_array_from_path(
                            "./templates/" + path + "/" + match_tiles
                        )
                        # total_score += self.compair(tile,tt)
                        score = max(self.compair(tile, tt), score)
                    # mean_score = total_score/num_tpl
                    if score > max_score:
                        max_score = score
                        target = path
                suit_s, order_s = target.split(".")[0].split("_")
                if suit_s not in ["black", "red"]:
                    order = Order.HUMAN
                else:
                    try:
                        detect = ocr.ocr(ex_tile)
                        order = Order(int(detect[0][0][1][0]))
                    except:
                        print(f"detect error at ({x},{y})")
                        order = Order(int(order_s))
                card = bot.Card(SUIT_MAP[suit_s], order)
                results.append(card)
        return results

    def load_array_from_path(self, path: str) -> np.ndarray:
        image: Image = PIL.Image.open(path)
        return np.array(image)

    def show_array(self, array: np.ndarray):
        image = PIL.Image.fromarray(array)
        image.save("temp_show.png")

    def compair(self, img1, img2) -> float:
        # 计算图img的直方图
        H1 = cv2.calcHist([img1], [0], None, [256], [0, 256])
        H1 = cv2.normalize(H1, H1, 0, 1, cv2.NORM_MINMAX, -1)  # 对图片进行归一化处理

        # 计算图img2的直方图
        H2 = cv2.calcHist([img2], [0], None, [256], [0, 256])
        H2 = cv2.normalize(H2, H2, 0, 1, cv2.NORM_MINMAX, -1)

        # 利用compareHist()进行比较相似度
        similarity = cv2.compareHist(H1, H2, 0)
        return similarity


if __name__ == "__main__":
    window = GameWindow.find_by_title(WINDOW_TITLE)
    window.activate()
    time.sleep(3)
    # image:Image = PIL.Image.open("./save.png")
    # if image.mode != "RGB":
    #         image = image.convert(mode="RGB")
    # window.prase_image(image)
    board = window.new_board_from_local("./save.png")
    # image = window.take_screenshot()

    # board = window.new_board()
    print(board)
    while not board.valid():
        text = input(">>>")
        if text == "done":
            break
        try:
            x, y, order_s = text.split(" ")
            x, y = int(x), int(y)
            order = Order(int(order_s))
            o_suit = board.grid[(x, y)].suit
            card = bot.Card(o_suit, order)
            board.grid[(x, y)] = card
            print(board)
        except:
            try:
                x, y, suit_s, order_s = text.split(" ")
                x, y = int(x), int(y)
                if suit_s not in ["black", "red"]:
                    order = Order.HUMAN
                else:
                    order = Order(int(order_s))
                card = bot.Card(SUIT_MAP[suit_s], order)
                board.grid[(x, y)] = card
                print(board)
            except:
                print("Error")
    moves = board.solve()
    # moves = [bot.Move((1,4),(-1,-1))]
    try:
        window.activate()
    except:
        print("Activate Error")
        input()
        time.sleep(10)
    time.sleep(3)
    window.send_moves(moves)
