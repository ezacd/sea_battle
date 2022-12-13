from random import randint
import time


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return 'Вы пытаетесь выстрелить за доску'


class BoardUsedException(BoardException):
    def __str__(self):
        return 'Вы уже стреляли в эту клетку'


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot: {self.x}, {self.y}'


class Ship:
    def __init__(self, bow, l, o):
        self.l = l
        self.o = o
        self.bow = bow
        self.xp = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i
            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shoot(self, shot):  # Dot(x, y)
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size
        self.count = 0

        self.map = [['O'] * size for _ in range(size)]
        self.busy = []
        self.ships_count = []

    def __str__(self):
        res = '  |'
        for i in range(self.size):
            res += f' {i} |'

        for i, row in enumerate(self.map):
            res += f'\n{i} | ' + ' | '.join(row) + ' |'

            if self.hid:
                res = res.replace('■', 'O')

        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):  # Ship(Dots(x, y), l, o)
        near = [(-1, -1), (-1, 0), (-1, 1),
                (0, -1), (0, 0), (0, 1),
                (1, -1), (1, 0), (1, 1)]

        for d in ship.dots:
            for dx, dy in near:
                con = Dot(d.x + dx, d.y + dy)

                if not (self.out(con)) and con not in self.busy:
                    if verb:
                        self.map[con.x][con.y] = '•'
                    self.busy.append(con)

    def add_ship(self, ship):  # Ship(Dot(x, y), l, o))
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException

        for d in ship.dots:
            self.map[d.x][d.y] = '■'
            self.busy.append(d)

        self.ships_count.append(ship)
        self.contour(ship)

    def shot(self, d):  # Dot(x, y)
        if self.out(d):
            raise BoardOutException
        if d in self.busy:
            raise BoardUsedException

        self.busy.append(d)

        for ship in self.ships_count:
            if d in ship.dots:
                ship.xp -= 1
                self.map[d.x][d.y] = 'X'
                if ship.xp == 0:
                    print('Корабль уничтожен')
                    time.sleep(1)
                    self.count += 1
                    self.contour(ship, verb=True)
                    return False
                else:
                    print('Корабль ранен')
                    time.sleep(1)
                    return True
        self.map[d.x][d.y] = '•'
        print('Мимо')
        time.sleep(1)
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход компьютера: {d.x}, {d.y}')
        return d


class User(Player):
    def ask(self):

        while True:
            cords = input('Введите координаты: ').split()

            if len(cords) != 2:
                print('Введите 2 координаты')
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print('Введите числа')
                continue

            x, y = int(x), int(y)

            return Dot(x, y)


class Game:
    def generate_board(self):
        ships_size = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)

        i = 0
        for size in ships_size:
            while True:
                i += 1
                if i > 1000:
                    return None

                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), size, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass

        board.begin()
        return board

    def try_board(self):
        board = None
        while board is None:
            board = self.generate_board()
        return board

    def __init__(self, size=6):
        self.size = size
        pl = self.try_board()
        ai = self.try_board()

        ai.hid = True

        self.ai = AI(ai, pl)
        self.pl = User(pl, ai)

    @staticmethod
    def greet():
        print("""
        Игра морской бой
          Формат ввода:
        х - номер строки
        у - номер столбца""")

    def loop(self):
        num = 0
        while True:
            print('-' * 20)
            print('Доска игрока')
            print(self.pl.board)
            print('-' * 20)
            print('Доска компьютера')
            print(self.ai.board)
            print('-' * 20)

            if num % 2 == 0:
                print('Ходит игрок')
                repeat = self.pl.move()
            else:
                print('Ходит компьютер')
                repeat = self.ai.move()
            if repeat:
                num -= 1
            if self.ai.board.count == 7:
                print('-' * 20)
                print('Игрок выиграл!')
                break

            if self.pl.board.count == 7:
                print('-' * 20)
                print('Компьютер выиграл!')
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
