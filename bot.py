import enum
import typing as t
import collections
import time

MAX_SOLVE_TIME = 180
GRID_X_LIMIT = 10
GRID_Y_LIMIT = 10


class Suit(str, enum.Enum):
    SPADE = "SPADE"  # 黑桃
    HEART = "HEART"  # 红桃
    DIAMOND = "DIAMOND"  # 方块
    CLUB = "CLUB"  # 梅花
    EMPTY = "EMPTY"  # 啥都没有
    BACK = "BACK"  # 牌背

    def __str__(self):
        return self.name


class Order(int, enum.Enum):
    HUMAN = 0
    TEN = 10
    NIN = 9
    OCT = 8
    SEV = 7
    SIX = 6
    NON = -1

    def __str__(self):
        return self.name


Coord: t.TypeAlias = t.Tuple[int, int]
Grid: t.TypeAlias = t.Dict[Coord, "Card"]


class Move(t.NamedTuple):
    start: Coord
    end: Coord


class Card:
    suit: Suit
    order: Order

    def __init__(self, suit: Suit, order: Order):
        self.suit = suit
        self.order = order

    def __hash__(self):
        return hash((self.suit, self.order))

    def __str__(self):
        return f"{self.suit}.{self.order}"

    def __eq__(self, value: object):
        if not isinstance(value, self.__class__):
            return NotImplemented
        return self.suit == value.suit and self.order == value.order

    def serialize(self) -> str:
        reds = [Suit.DIAMOND, Suit.HEART]
        blacks = [Suit.SPADE, Suit.CLUB]
        if self.order == Order.HUMAN:
            name = self.suit[:3]
        elif self.order == Order.NON:
            name = "---"
        else:
            o = "%02d" % int(self.order)
            if self.suit in reds:
                s = "R"
            elif self.suit in blacks:
                s = "B"
            name = f"{s}{o}"
        if self.suit in reds:
            name = "\033[31m" + name + "\033[0m"
        elif self.suit in blacks:
            name = "\033[2m" + name + "\033[0m"
        elif self.suit == Suit.BACK:
            name = "\033[43m" + name + "\033[0m"
        else:
            name = "\033[2m" + name + "\033[0m"
        return name

    @classmethod
    def empty(cls) -> "Card":
        return cls(Suit.EMPTY, Order.NON)

    @classmethod
    def back(cls) -> "Card":
        return cls(Suit.BACK, Order.NON)

    @property
    def isEmpty(self) -> bool:
        return self.suit == Suit.EMPTY

    @property
    def isBack(self) -> bool:
        return self.suit == Suit.BACK

    def follow(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        if self.order == Order.NON:
            return False
        elif self.order == Order.HUMAN:
            return self == other
        else:
            reds = [Suit.DIAMOND, Suit.HEART]
            blacks = [Suit.SPADE, Suit.CLUB]
            if self.suit in reds and other.suit in reds:
                return False
            elif self.suit in blacks and other.suit in blacks:
                return False
            return self.order - 1 == other.order


class Board:
    def __init__(
        self, grid: t.Optional[Grid] = None, moves: t.Optional[t.List[Move]] = None
    ):
        self.grid: Grid = self.init_grid() if grid is None else grid
        self._moves: t.List[Move] = [] if moves is None else moves

    @property
    def id(self) -> object:
        """Identity when solving the board, ignores moves list"""
        return frozenset((coord, card) for (coord, card) in self.grid.items() if card)

    @property
    def moves(self) -> t.List[Move]:
        return self._moves

    def init_grid(self) -> Grid:
        grid = {}
        grid[(-1, -1)] = Card.empty()
        for i in range(1, GRID_X_LIMIT):
            for j in range(1, GRID_Y_LIMIT):
                grid[(i, j)] = Card.empty()
        return grid

    def clone(self) -> "Board":
        return self.__class__(
            self.grid.copy(),
            self.moves.copy(),
        )

    def done(self) -> bool:
        def check_inorder(col) -> bool:
            last = self.grid.get((col, 1))
            if not last:
                return False
            if last.isEmpty or last.isBack:
                return False
            for y in range(2, 6):  # 检查牌能否堆叠。
                next = self.grid.get((col, y))
                if not next:
                    return False
                if next.isEmpty or next.isBack:
                    return False
                if not last.follow(next):
                    return False
                last = next
            return True

        if not self.grid.get((-1, -1)).isEmpty:
            return False
        num_cal = 0
        bac_cal = 0
        for x in range(1, GRID_X_LIMIT):
            num_cal += check_inorder(x)
            bac_cal += self.grid.get((x, 1)).isBack
        return num_cal == 4 and bac_cal == 4

    def valid(self) -> bool:
        tar_cal = {
            (Suit.CLUB, Order.HUMAN): 4,
            (Suit.SPADE, Order.HUMAN): 4,
            (Suit.HEART, Order.HUMAN): 4,
            (Suit.DIAMOND, Order.HUMAN): 4,
            (Suit.HEART, Order.TEN): 2,
            (Suit.HEART, Order.NIN): 2,
            (Suit.HEART, Order.OCT): 2,
            (Suit.HEART, Order.SEV): 2,
            (Suit.HEART, Order.SIX): 2,
            (Suit.SPADE, Order.TEN): 2,
            (Suit.SPADE, Order.NIN): 2,
            (Suit.SPADE, Order.OCT): 2,
            (Suit.SPADE, Order.SEV): 2,
            (Suit.SPADE, Order.SIX): 2,
        }
        cal = {
            (Suit.CLUB, Order.HUMAN): 0,
            (Suit.SPADE, Order.HUMAN): 0,
            (Suit.HEART, Order.HUMAN): 0,
            (Suit.DIAMOND, Order.HUMAN): 0,
            (Suit.HEART, Order.TEN): 0,
            (Suit.HEART, Order.NIN): 0,
            (Suit.HEART, Order.OCT): 0,
            (Suit.HEART, Order.SEV): 0,
            (Suit.HEART, Order.SIX): 0,
            (Suit.SPADE, Order.TEN): 0,
            (Suit.SPADE, Order.NIN): 0,
            (Suit.SPADE, Order.OCT): 0,
            (Suit.SPADE, Order.SEV): 0,
            (Suit.SPADE, Order.SIX): 0,
        }
        for card in self.grid.values():
            if card.isEmpty:
                continue
            cal[(card.suit, card.order)] += 1
        return cal == tar_cal

    def solve(self) -> t.List[Move]:
        return solve(self)

    def move(self, move: Move) -> bool:
        self._moves.append(move)
        ori, tar = move
        if not self.check_movable(move):
            return False
        for y_offset in range(GRID_Y_LIMIT):
            ori_c = self.grid.get((ori[0], ori[1] + y_offset))
            tar_c = self.grid.get((tar[0], tar[1] + y_offset))
            if not ori_c or not tar_c:
                break
            if ori_c.isEmpty:
                break
            self.grid[(tar[0], tar[1] + y_offset)] = ori_c
            self.grid[(ori[0], ori[1] + y_offset)] = Card.empty()
        return self.check_stack(tar[0]) if tar[0] != -1 else True

    def check_stack(self, col: int) -> bool:
        assert 0 < col and col < 10
        head = self.grid.get((col, 1))
        if not head:
            return False
        if head.order != Order.HUMAN:
            return False
        for y in range(2, 5):
            card = self.grid.get((col, y))
            if not card:
                return False
            if card != head:
                return False
        for y in range(2, 5):
            self.grid[(col, y)] = Card.empty()
        self.grid[(col, 1)] = Card.back()
        return True

    def find_move(self) -> t.List[Move]:
        moves = []
        for coord_s in self.grid.keys():
            for coord_t in self.grid.keys():
                if self.check_movable((coord_s, coord_t)):
                    moves.append(Move(coord_s, coord_t))
        return moves

    def check_movable(self, move: Move) -> bool:
        # check origin
        ori, tar = move
        if tar == (-1, -1):
            pass
        if ori == tar:
            return False
        origin = self.grid.get(ori)
        if not origin:
            return False
        if origin.isEmpty or origin.isBack:
            return False
        col = ori[0]
        numstack = 1
        last = origin
        toexcept: t.List[t.Tuple[Coord]] = [ori]  # 被拿起来的牌要除外
        if ori != (-1, -1):  # 右上角不需要检查
            for y in range(ori[1] + 1, GRID_Y_LIMIT):  # 检查牌能否堆叠。
                next = self.grid.get((col, y))
                if next.isEmpty:
                    break
                if not last.follow(next):
                    return False
                toexcept.append((col, y))
                last = next
                numstack += 1

        temp_board = self.clone()
        for cor in toexcept:
            temp_board.grid[cor] = Card.empty()

        # check target
        target = temp_board.grid.get(tar)
        target_top = temp_board.grid.get((tar[0], tar[1] - 1))
        if not target:
            return False
        elif not target.isEmpty or target.isBack:
            return False
        elif tar[1] == 1:
            return True
        elif tar[1] == -1 and numstack == 1:
            return True
        elif target_top and target_top.follow(origin):
            return True
        else:
            return False

    def __eq__(self, value):
        if not isinstance(value, self.__class__):
            return NotImplemented
        return self.grid == value.grid

    def __hash__(self) -> int:
        return hash(self.id)

    def __str__(self) -> str:
        return self.serialize(sep="\n")

    def serialize(self, sep: str = "\n") -> str:
        return (
            sep.join(
                " ".join(
                    self.grid.get((col, row)).serialize()
                    for col in range(1, GRID_X_LIMIT)
                )
                for row in range(1, GRID_Y_LIMIT)
            )
            + sep
            + self.grid.get((-1, -1)).serialize()
            + sep
        )


def solve(
    board: Board, max_solve_time: int = MAX_SOLVE_TIME, debug=False
) -> t.List[Move]:
    boards: t.Set[Board] = {board}
    queue: t.Deque[Board] = collections.deque([board])
    steps = 0
    st = time.time()
    done = False
    moves = []
    while queue and not done:
        if time.time() - st > max_solve_time:
            print("\nTimeout!")
            break

        # if debug:
        parent = queue.pop()  # DFS
        print(
            f"\rdepth: {len(parent.moves)}, boards: {len(boards)}, to solve: {len(queue)}\t\t",
            end="",
        )
        if len(parent.moves) > 1000:  # 深度限制
            print("\nDepth limit!")
            break
        length = len(parent.moves)
        if steps < length + 1:
            steps = length + 1
        found_moves = parent.find_move()
        if debug:
            print(parent, found_moves)
            input()
        for move in found_moves:
            board, done = solve_move(parent, move, boards)
            if debug:
                print(move, done, board is not parent, len(queue))
                print(board)
                input()
            if done:
                moves = board.moves
                break
            if board is not parent:
                boards.add(board)
                queue.append(board)
    if done:
        print("\nDone!")
        print(moves)
        nt = time.time()
        print(
            "\n%.2fs, %d boards (%.2f boards/s), %d moves deep"
            % (nt - st, len(boards), (nt - st) / min(1, len(boards)), len(moves))
        )
    else:
        print("\nFail!\n")
    return moves


def solve_move(parent: Board, move: Move, boards: t.Set[Board]) -> t.Tuple[Board, bool]:
    board = parent.clone()
    board.move(move)
    if board in boards:
        return parent, False
    return board, board.done()
