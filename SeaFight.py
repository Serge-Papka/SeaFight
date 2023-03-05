cells = 6  # Поле 6*6


try:
    class Dot():
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __eq__(self, other):
            return self.x == other.x and self.y == other.y

        def __str__(self):
            return f'Dot: {self.x, self.y}'


    class Ship():
        def __init__(self, length=1, stem=(0, 0), rotate=0, hp=1):  # rotate 90 = вверх(градусы)
            self.length = length
            self.stem = stem
            self.rotate = rotate
            self.hp = hp

        def dots(self):
            dots_list = []
            for i in range(self.length):
                if self.aflat:
                    dots_list = dots_list + [(self.stem[0] + i, self.stem[1])]
                else:
                    dots_list = dots_list + [(self.stem[0], self.stem[1] + i)]
            return dots_list
            # huricane = Ship(2, (1, 1), 1, 10)
            # print(huricane.dots())


    def remove_mistakes(list_):
        miss = [' ', '-', '+', '*', '**', '/', '|', '=', '.', ",", '', '', '', '', ]
        for i in miss:
            while True:
                if list_.count(i):
                    list_.remove(i)
                else:
                    break
        return list_


    class Board():
        def __init__(self, hid=True, ships=[3, 2, 2, 1, 1, 1, 1], ship_l=7):
            self.ships = ships
            self.hid = hid
            self.ship_l = ship_l
            self.pole = []
            line_pole = []
            for i in range(cells + 1):
                for j in range(cells + 1):
                    if i == 0 and j != 0:  # Шапка горизонт
                        line_pole.append(chr(64 + j))
                    elif i != 0 and j == 0:  # Шапка вертикаль
                        line_pole.append(str(i))
                    else:
                        line_pole.append(' ')
                self.pole.append(line_pole)
                line_pole = []

        def add_ship(self):

            for ship in self.ships:
                steam = list(input(
                    f"Установка {ship}-клеточного корабля.\n"
                    f"Введите корды носа(En) от A1 до {chr(64 + cells)}{cells} : "))
                steam = remove_mistakes(steam)
                print(steam)


            # self.A
            pass

        def __str__(self):
            show = ''
            for i, value_1 in enumerate(self.pole):
                for j, value_2 in enumerate(self.pole[i]):
                    if i == 0:
                        show = show + ''.join(self.pole[i][j]) + '   '
                    else:
                        show = show + ''.join(self.pole[i][j]) + ' | '
                show = show + '\n'
            return show


    B1 = Board()
    print(str(B1))
    B1.add_ship()

    # print(B1.ship_l)
    # print(B1.ships)

    print(str(B1))
except IndexError:
    print("BoardOutException")
