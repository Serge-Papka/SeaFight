from random import randint, randrange
import time

cells = 6  # Поле 6*6
think_time_pc = 1
difficult = 2  # 1='easy', 2='normal', 3='hardcore'
# Хардкор заработает, когда пройдёшь игру на normal...(joke.не заработает, он еще не создан))

free_block = round((cells ** 2) / 9)  # Конструктор кораблей поля, для поля 6*6 = [3, 2, 2, 1, 1, 1, 1]
ships_pattern = [1] + [1] * (free_block + round(cells / 2) - 1)
while free_block >= 1:
    for i in range(round(free_block * 0.75)):
        ships_pattern[i] += 1
        free_block -= 1


class MyExceptions(Exception):
    pass


class BoardOutException(MyExceptions):
    def __str__(self):
        return "Координаты вне игрового поля"


class DoubleShoot(MyExceptions):
    def __str__(self):
        return "В эту точку вы уже стреляли"


class ShipCantPlace(MyExceptions):
    pass


class Ship:
    def __init__(self, length=1, bow=(1, 1), rotate=1):  # rotate 0 = вправо,1 вверх,2 лево,3 низ
        self.length = length
        self.bow = bow
        self.hp = length
        if (rotate >= 0) and (rotate < 4):
            self.rotate = rotate
        else:
            print(rotate)
            print("Поворот Не от 0 до 4")

    def dots(self):
        dots_ship = []
        for i in range(self.length):
            if self.rotate == 0:
                dots_ship = dots_ship + [(self.bow[0] + i, self.bow[1])]
            elif self.rotate == 1:
                dots_ship = dots_ship + [(self.bow[0], self.bow[1] + i)]
            elif self.rotate == 2:
                dots_ship = dots_ship + [(self.bow[0] - i, self.bow[1])]
            else:
                dots_ship = dots_ship + [(self.bow[0], self.bow[1] - i)]
        return dots_ship


def remove_mistakes(list_):  # Удаляю лишние символы и возвращаю буквы в верхнем регистре.
    miss = [' ', '-', '+', '*', '**', '/', '|', '=', '.', ",", '', '', '', '', ]
    for i_str in miss:
        while True:
            if list_.count(i_str):
                list_.remove(i_str)
            else:
                break
    for i in range(len(list_)):
        list_[i] = list_[i].upper()
    return list_


def change_to_dot(list_):
    if list_[1].isdigit():
        if not (list_[0].isdigit()):  # (буква,цифра)
            list_[0], list_[1] = int(list_[1]), ord(list_[0]) - 64
        else:  # Если введут стандартные координаты (цифра,цифра)
            list_[0], list_[1] = int(list_[0]), int(list_[1])
    elif list_[0].isdigit():  # (цифра,буква)
        list_[0], list_[1] = int(list_[0]), ord(list_[1]) - 64
    list_ = (list_[0], list_[1])
    return list_


class Board:
    def __init__(self, hid=False, alive_ships=7):
        self.pole = []  # 1. Двумерный список, в котором хранятся состояния каждой из клеток.
        for i in range(cells + 1):
            line_pole = []
            for j in range(cells + 1):
                if i == 0 and j != 0:  # Шапка горизонт
                    line_pole.append(chr(64 + j))
                elif i != 0 and j == 0:  # Шапка вертикаль
                    line_pole.append(str(i))
                else:
                    line_pole.append(' ')
            self.pole.append(line_pole)
        self.ships = []  # 2. Список кораблей доски.
        self.hid = hid  # 3. скрывать корабли
        self.alive_ships = alive_ships  # 4. Количество живых кораблей на доске.
        self.not_free = []  # Занятые клетки для строительства
        self.shot_through = []  # Прострелянные клетки
        self.wounded = []  # Раненый

    def add_ship(self, ship):
        for i_dot in ship.dots():
            if self.out(i_dot):
                raise ShipCantPlace
            if i_dot in self.not_free:
                raise ShipCantPlace
        for i_dot in ship.dots():
            self.pole[i_dot[0]][i_dot[1]] = "■"
            self.not_free.append(i_dot)
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, marker="."):
        for center in ship.dots():
            for i in range(center[0] - 1, center[0] + 2):
                for j in range(center[1] - 1, center[1] + 2):
                    if marker != "." and not (self.out((i, j))):
                        if self.hid:  # нам обводить убитые, но не запрещать стрелять; компу запрещать, но не обводить.
                            if self.pole[i][j] == ".":
                                self.pole[i][j] = marker
                        else:
                            if difficult > 1:
                                if not ((i, j) in self.shot_through):
                                    self.shot_through.append((i, j))
                    if not ((self.out((i, j))) or ((i, j) in self.not_free)):
                        self.pole[i][j] = marker
                        self.not_free.append((i, j))

    def contour_d(self, x, y):
        for ip in [-1, 1]:
            for jp in [-1, 1]:
                if not ((self.out((x + ip, y + jp))) or ((x + ip, y + jp) in self.shot_through)):
                    self.shot_through.append((x + ip, y + jp))

    def __str__(self):
        show = ''
        for i, value_1 in enumerate(self.pole):
            for j, value_2 in enumerate(self.pole[i]):
                point = self.pole[i][j]
                point = point.replace(".", " ")
                if self.hid:
                    point = point.replace("■", " ")
                if i == 0:
                    show = show + ''.join(point) + '   '
                else:
                    if j == 0 and len(value_2) > 1:  # Уменьшить отступ для 2-х значных чисел шапки
                        show = show + ''.join(point) + '| '
                    else:
                        show = show + ''.join(point) + ' | '
            show = show + '\n'
        return show[:-2] + ' '

    @staticmethod
    def out(point):
        return not ((0 < point[0] <= cells) and (0 < point[1] <= cells))

    def shot(self, point):
        player = ("    " * (cells + 3) + "Игрок") if self.hid else "\nКомп"
        if self.out(point):
            raise BoardOutException
        if point in self.shot_through:
            raise DoubleShoot
        self.shot_through.append(point)
        for ship in self.ships:
            if point in ship.dots():
                ship.hp -= 1
                if not self.hid:
                    if difficult > 1:
                        self.contour_d(point[0], point[1])
                self.pole[point[0]][point[1]] = 'x'
                if ship.hp == 0:
                    self.alive_ships -= 1
                    print(f"{player} стрельнул {chr(point[1] + 64)}{point[0]} - убил!")
                    self.contour(ship, marker='°')  # °
                    if not self.hid:
                        self.wounded = []  # обнуление раненого
                    if self.alive_ships == 0:
                        return False
                    return True
                else:
                    print(f"{player} стрельнул {chr(point[1] + 64)}{point[0]} - попал!")
                    if not self.hid:
                        self.wounded.append((point[0], point[1]))
                    return True
        self.pole[point[0]][point[1]] = '·'
        print(f"{player} стрельнул {chr(point[1] + 64)}{point[0]} - мимо!")
        return False


class Player:
    def __init__(self, board_player, board_enemy):
        self.board_player = board_player
        self.board_enemy = board_enemy

    def ask(self):
        print('Этот метод переопределён')

    def move(self):
        while True:
            repeater = True
            while repeater:
                try:
                    point = self.ask()
                    repeater = self.board_enemy.shot(point)
                    gamer.show()
                    if self.board_enemy.alive_ships == 0:
                        return False

                    if (repeater and self.board_player.hid) or not (repeater or self.board_player.hid):
                        time.sleep(think_time_pc)
                    if not repeater:
                        return False
                except MyExceptions as e:
                    if not self.board_player.hid:  # В ход компа не выводить ошибки.
                        print(e)


class AI(Player):
    def ask(self):
        while True:
            if gamer.board_user.wounded and difficult > 1:  # есть раненый
                if len(gamer.board_user.wounded) == 1:
                    dot = (gamer.board_user.wounded[0][0], gamer.board_user.wounded[0][1])
                    rnd = randint(0, 1)
                    if rnd == 1:
                        shot = (dot[0] + randrange(-1, 2, 2), dot[1])
                    else:
                        shot = (dot[0], dot[1] + randrange(-1, 2, 2))
                else:
                    len_ = len(gamer.board_user.wounded)
                    dot = (gamer.board_user.wounded[0][0], gamer.board_user.wounded[0][1])
                    dot2 = (gamer.board_user.wounded[len_ - 1][0], gamer.board_user.wounded[len_ - 1][1])
                    if dot[0] == dot2[0]:  # раненый корабль горизонтальный
                        if dot[1] > dot2[1]:
                            dot, dot2 = dot2, dot  # ставлю по возрастанию
                        shot = (dot[0], (randrange(dot[1] - 1, dot2[1] + 2, len_ + 1)))
                    else:
                        if dot[0] > dot2[0]:
                            dot, dot2 = dot2, dot
                        shot = ((randrange(dot[0] - 1, dot2[0] + 2, len_ + 1)), dot[1])
            else:
                shot = (randint(1, cells), randint(1, cells))
            return shot


class User(Player):
    def ask(self):
        while 1:
            shot = list(input(f"Ваш ход: "))
            shot = remove_mistakes(shot)
            if len(shot) < 2:
                print("Нужно 2 координаты")
                continue
            elif len(shot) > 2:  # Соберу все буквы и цифры, сделаю из них координаты: 12a or a12 or 1a2 -> A12
                letter = 0
                numbers = []
                if shot == ['7', '7', '7']:
                    for rep in range(2):
                        if not gamer.board_pc.hid:
                            gamer.board_pc.hid = True
                        else:
                            gamer.board_pc.hid = False
                        print("Чит-тест" + "\n" * 10)
                        gamer.show()
                        if rep == 0:
                            time.sleep(1)
                    continue
                for j in range(len(shot)):
                    if not (shot[j].isdigit()):
                        letter += 1
                        shot[0] = shot[j]
                    else:
                        numbers.append(shot[j])
                if letter > 1:
                    print("Нужно только одну букву")
                    continue
                if letter == 0:
                    print("Нужно хотя бы одну букву")
                    continue
                shot[1] = ''.join(numbers)
            shot = change_to_dot(shot)
            if isinstance(shot[0], str) and isinstance(shot[1], str):
                print("Нужно хотя бы 1 цифру")
                continue
            return shot


class Game:
    def __init__(self):
        self.board_pc = self.random_board(True)  # True \ False - скрыть корабли врага
        self.board_user = self.random_board()
        self.user = User(self.board_user, self.board_pc)
        self.pc = AI(self.board_pc, self.board_user)

    @staticmethod
    def random_board(hid=False):
        while True:
            correct = 0
            bord = Board(hid, alive_ships=len(ships_pattern))
            for len_ in ships_pattern:
                counter = 0
                while True:
                    ship = Ship(length=len_, bow=(randint(1, cells), randint(1, cells)),
                                rotate=randint(0, 1))
                    try:
                        counter += 1
                        bord.add_ship(ship)
                        correct += 1
                        break
                    except ShipCantPlace:
                        pass
                    if counter >= 2000:
                        break
                if counter >= 2000:
                    break
            if correct == len(ships_pattern):
                break
        return bord

    def show(self):
        list_b1 = self.board_user.__str__().split('\n') + ["  " * (cells // 2) + "Ваше поле"]
        list_b2 = self.board_pc.__str__().split('\n') + ["    " * (cells - 1) + "Поле врага"]
        for m, value in enumerate(list_b1):
            print(f"{list_b1[m]}        {list_b2[m]}")

    def greet(self):
        print("")
        print("                         Морской Бой.")
        print(f"        Для выстрела введите координаты(En) от A1 до {chr(64 + cells)}{cells}")
        print("")
        self.show()

    def loop(self):
        while True:
            self.user.move()
            if self.board_pc.alive_ships == 0:
                print("Победил игрок")
                return

            self.pc.move()
            if self.board_user.alive_ships == 0:
                print("    " + "    " * cells * 2 + "Победил комп")
                break

    def start(self):
        self.greet()
        self.loop()


gamer = Game()
gamer.start()
