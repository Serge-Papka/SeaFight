from random import randint, randrange
import time

cells = 6  # Поле 6*6
think_time_pc = 0.00001
difficult = 3  # 1='easy', 2='normal', 3='hardcore'
# Хардкор заработает, когда пройдена игра на normal...(joke.не заработает, он еще не создан))

free_block = round((cells ** 2) / 9)  # Конструктор кораблей поля, для поля 6*6 = [3, 2, 2, 1, 1, 1, 1]
ships_pattern = [1] + [1] * (free_block + round(cells / 2) - 1)
while free_block >= 1:
    for i in range(round(free_block * 0.75)):
        ships_pattern[i] += 1
        free_block -= 1


# print(ships_pattern)


class MyExceptions(Exception):
    pass


class BoardOutException(MyExceptions):
    def __str__(self):
        return "Координаты вне игрового поля"


class DoubleShoot(MyExceptions):
    def __str__(self):
        return "В эту точку вы уже стреляли"


class ShipCantPlace(MyExceptions):
    # def __str__(self):  # Удалить перед сдачей
    #     return "Тест ошибка постановки корабля"  # Удалить перед сдачей
    pass


class Dot:  # В игре не использовал этот класс, вместо него функция change_to_dot()
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f'Dot: {self.x, self.y}'


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
        # huricane = Ship(2, (1, 1), 1)
        # print(huricane.dots())


def remove_mistakes(list_):  # Удаляю лишние символы и возвращаю буквы в верхнем регистре.
    miss = [' ', '-', '+', '*', '**', '/', '|', '=', '.', ",", '', '', '', '', ]
    for i in miss:
        while True:
            if list_.count(i):
                list_.remove(i)
            else:
                break
    for i in range(len(list_)):
        list_[i] = list_[i].upper()
    return list_


def change_to_dot(list_):
    if list_[1].isdigit():
        if not (list_[0].isdigit()):  # (буква,цифра)
            list_[0], list_[1] = int(list_[1]), ord(list_[0]) - 64
            # print(list_,404)
        else:  # Если введут стандартные координаты (цифра,цифра)
            list_[0], list_[1] = int(list_[0]), int(list_[1])
    elif list_[0].isdigit():  # (цифра,буква)
        list_[0], list_[1] = int(list_[0]), ord(list_[1]) - 64
    # else:  # (буква,буква) ?)    Раскомментировать 3 строчки , чтоб переводил 2 буквы в 2 циры
    #     print(f"меняю {list_[1]} на {ord(list_[1])-64}")  #  раскомментировать
    #     list_[0], list_[1] = ord(list_[1]) - 64, ord(list_[0]) - 64  #  раскомментировать
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
        self.shooten = []  # Прострелянные клетки
        self.wounded = []  # Раненый

    def add_ship(self, ship):
        for i in ship.dots():
            if self.out(i):
                raise ShipCantPlace
            if i in self.not_free:
                raise ShipCantPlace
        for i in ship.dots():
            # print(self.pole[0][0])
            self.pole[i[0]][i[1]] = "■"
            # print('dfgdfgfdg',[i[0]], [i[1]])
            self.not_free.append(i)
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, marker="."):
        for center in ship.dots():
            # print("Центр", center)
            for i in range(center[0] - 1, center[0] + 2):
                for j in range(center[1] - 1, center[1] + 2):
                    # print("Вот", i, j)
                    if marker != "." and not (self.out((i, j))):
                        if self.hid:  # нам обводить убитые, но не запрещать стрелять; компу запрещать, но не обводить.
                            if self.pole[i][j] == ".":
                                self.pole[i][j] = marker
                        else:
                            if difficult > 1:
                                if not ((i, j) in self.shooten):
                                    self.shooten.append((i, j))
                    if not ((self.out((i, j))) or ((i, j) in self.not_free)):
                        # print("Аут в контуре:", self.out((i, j)))
                        # print((i, j) in self.not_free)

                        # print((i, j))
                        self.pole[i][j] = marker
                        self.not_free.append((i, j))
                        # print(self.not_free)

    def contour_d(self, x, y):
        for ip in [-1, 1]:
            for jp in [-1, 1]:
                if not ((self.out((x + ip, y + jp))) or ((x + ip, y + jp) in self.shooten)):
                    self.shooten.append((x + ip, y + jp))

    def __str__(self):
        show = ''
        for i, value_1 in enumerate(self.pole):
            for j, value_2 in enumerate(self.pole[i]):
                point = self.pole[i][j]
                point = point.replace(".", " ")
                if self.hid:
                    # print('1wwewq')
                    point = point.replace("■", " ")
                    # print (point)
                if i == 0:
                    show = show + ''.join(point) + '   '
                else:
                    if j == 0 and len(value_2) > 1:  # Уменьшить отступ для 2х значных чисел шапки
                        show = show + ''.join(point) + '| '
                    else:
                        show = show + ''.join(point) + ' | '
            show = show + '\n'
        return show[:-2] + ' '

    def out(self, point):
        # print(point, 666)
        # print(point[0])
        # print(point[1])
        # print(0 < point[0] <= cells)
        # print(0 < point[1] <= cells)
        # print(not ((0 < point[0] <= cells) and (0 < point[1] <= cells)))
        # print("Точка аута:", not ((0 < point[0] <= cells) and (0 < point[1] <= cells)))
        return not ((0 < point[0] <= cells) and (0 < point[1] <= cells))

    def shot(self, point):
        player = ("    " * (cells + 3) + "Игрок") if self.hid else "\nКомп"
        if self.out(point):
            raise BoardOutException
        if point in self.shooten:
            raise DoubleShoot
        self.shooten.append(point)
        for ship in self.ships:
            # print(point, 1)
            # print(ship.dots(), 2)
            # print(ship.hp, 3)
            if point in ship.dots():
                ship.hp -= 1
                if not self.hid:
                    if difficult > 1:
                        self.contour_d(point[0], point[1])
                # print(self.pole)
                # print('fghfgh',(point[0], point[1]))
                # print(self.pole[0][0])
                # print(self.pole[point[0]][point[1]])#= "fgdhdfghdfg"
                self.pole[point[0]][point[1]] = 'x'
                if ship.hp == 0:
                    self.alive_ships -= 1
                    print(f"{player} стрельнул {chr(point[1] + 64)}{point[0]} - убил!")
                    self.contour(ship, marker='°')  # °
                    # if not self.hid:
                    #     gamer.show()
                    #     time.sleep(think_time_pc)
                    if not self.hid:
                        self.wounded = []  # обнуление раненого
                    if self.alive_ships == 0:
                        return False
                    return True
                else:
                    print(f"{player} стрельнул {chr(point[1] + 64)}{point[0]} - попал!")
                    if not self.hid:
                        print(555666)
                        self.wounded.append((point[0], point[1]))
                    print(self.wounded, 555666)
                    # if not self.hid:
                    #     gamer.show()
                    #     time.sleep(think_time_pc)
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
        # raise NotImplementedError()

    def move(self):
        while True:
            repeater = True
            while repeater:
                try:
                    point = self.ask()
                    repeater = self.board_enemy.shot(point)
                    gamer.show()
                    # print(repeater,67)
                    # print(self.board_player.hid,67)
                    # print(repeater and self.board_player.hid)
                    # print(not(repeater and self.board_player.hid))
                    if self.board_enemy.alive_ships == 0:
                        # print(self.board_enemy.alive_ships, "self.board_enemy.alive_ships")
                        return False

                    if (repeater and self.board_player.hid) or not (repeater or self.board_player.hid):
                        # print('67')
                        time.sleep(think_time_pc)
                    # print(self.board_player.hid)
                    if not repeater:
                        return False
                    # gamer.show()
                except MyExceptions as e:
                    if not self.board_player.hid:  # В ход компа не выводить ошибки.
                        print(e, "123")


#
class AI(Player):
    def ask(self):
        while True:
            print(gamer.board_user.wounded, 'sadasdas')
            # dot = []
            # dot2 = []
            if gamer.board_user.wounded and difficult > 1:  # есть раненый
                print(gamer.board_user.wounded, 954161165156)
                if len(gamer.board_user.wounded) == 1:
                    print(333)
                    # print(gamer.board_user.wounded[0][0],9090)
                    # print(gamer.board_user.wounded[1],9898)
                    # print((gamer.board_user.wounded[0], gamer.board_user.wounded[1]),777555)
                    dot = (gamer.board_user.wounded[0][0], gamer.board_user.wounded[0][1])
                    print(dot, 'dot333')
                    # for ip in [-1, 1]:
                    #     for jp in [-1, 1]:
                    rnd = randint(0, 1)
                    print(rnd)
                    if rnd == 1:
                        shot = (dot[0] + randrange(-1, 2, 2), dot[1])
                    else:
                        shot = (dot[0], dot[1] + randrange(-1, 2, 2))



                else:
                    print(len(gamer.board_user.wounded), 444)
                    len_ = len(gamer.board_user.wounded)
                    dot = (gamer.board_user.wounded[0][0], gamer.board_user.wounded[0][1])
                    dot2 = (gamer.board_user.wounded[len_ - 1][0], gamer.board_user.wounded[len_ - 1][1])
                    print(dot, 11)
                    print(dot2, 22)
                    if dot[0] == dot2[0]:  # раненый корабль горизонтальный
                        if dot[1] > dot2[1]:
                            dot, dot2 = dot2, dot  # ставлю по возрастанию
                        print(654)
                        shot = (dot[0], (randrange(dot[1] - 1, dot2[1] + 2, len_+1)))
                    else:
                        print(456)
                        if dot[0] > dot2[0]:
                            dot, dot2 = dot2, dot
                        shot = ((randrange(dot[0] - 1, dot2[0] + 2, len_+1)), dot[1])

            else:
                shot = (randint(1, cells), randint(1, cells))

            print(f"Ход компьютера: {chr(shot[1] + 64)} {shot[0]} ")
            print(shot)
            time.sleep(0.01)
            return shot
            print(9999999999999999999)


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
            # print(shot, 44)
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
                    ship = Ship(length=len_, bow=(randint(1, cells), randint(1, cells)), rotate=randint(0, 1))
                    # print(len_,counter, ship.dots())
                    try:
                        counter += 1
                        bord.add_ship(ship)
                        correct += 1
                        break
                    except ShipCantPlace as e:
                        pass
                    if counter >= 2000:
                        break
                if counter >= 2000:
                    break
            if correct == len(ships_pattern):
                break
        # print(bord.ships.__str__())
        # print(bord.alive_ships)
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
        while True:  # self.board_user.alive_ships > 0 and self.board_pc.alive_ships > 0:
            # self.user.move()
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

#
# B1 = Board()
# B2 = Board()
# # print(str(B1))
# ship55 = Ship(5, (3, 5), 3)
# # print(ship55.dots())
#
# B1.add_ship(ship55)
# # print(B1.not_free)
#
#
# # print(B1.ship_l)
# # print(B1.ships)
# # print(str(B1))
# # B1.shot((3,1))
# # B1.shot((3,2))
# # B1.shot((3,3))
# # B1.shot((3,4))
# # B1.shot((3,5))
# #
# #
# # B1.shot((5,1))
# # print(B1.shooten)
# im = User(B1, B2)
# im.move()
# print(str(B1))
# print(str(B2))
# print("Конец")
