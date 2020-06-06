# импортируем нужные библиотеки

import argparse
import json
import random
import arcade as ar
import numpy as np

# создаем входной параметр - название сохранения

parser = argparse.ArgumentParser(description='call file')
parser.add_argument("-f", "--file", type=str,
                    help="name.json", default="version.json")
args = parser.parse_args()


# создаем функции для сохранения таблицы в файл


def load():
    try:
        with open(args.file, "r") as file:
            version = json.load(file)
            return np.array(version, dtype=np.int)
    except FileNotFoundError:
        return []


def save(version):
    with open(args.file, "w") as file:
        json.dump(version.tolist(), file)


# создаем функцию для проверки пустых ячеек


def test(mas):
    empty = []
    for i in range(4):
        for j in range(4):
            if mas[i][j] == 0:
                num = number(i, j)
                empty.append(num)
    return empty


def number(i, j):
    return i * 4 + j + 1


def index(num):
    num -= 1
    x, y = num // 4, num % 4
    return x, y


# создаем функцию для появления 2(80% вероятность)
# или 4 в случайной пустой ячейке


def insert(mas):
    empty = test(mas)
    n = random.choice(empty)
    x, y = index(n)
    if np.random.sample() <= 0.8:
        mas[x][y] = 2
    else:
        mas[x][y] = 4
    return mas


# создаем пустую таблицу 4 на 4


start = np.zeros((4, 4), dtype=np.int)

# проверяем, есть ли сохранение, иначе создаем новое

version = load()
if version != []:
    game = version
else:
    game = insert(np.copy(start))

# создаем словарь цветов, а также некоторые сокращения #

colort = ar.csscolor.TURQUOISE
colormt = ar.csscolor.MEDIUM_TURQUOISE
colorw = ar.color.WHITE
colorb = ar.color.BLACK

d_color = {
    2: ar.csscolor.DEEP_PINK,
    4: ar.csscolor.CYAN,
    8: ar.csscolor.DEEP_SKY_BLUE,
    16: ar.csscolor.MEDIUM_SPRING_GREEN,
    32: ar.csscolor.DARK_VIOLET,
    64: ar.csscolor.LIME,
    128: ar.csscolor.BLUE,
    256: ar.csscolor.MAGENTA,
    512: ar.csscolor.SILVER,
    1024: ar.csscolor.GOLD,
    2048: ar.csscolor.DARK_RED
}


# создаем функции сдвигов ячеек со сложением
# одинаковых степеней двоек


def shift(st):
    a = []
    for i in range(4):
        if st[i] == 0:
            a.append(i)
    st = np.delete(st, a)
    st = np.append(st, np.zeros(4 - len(st), dtype=np.int))
    for i in range(3):
        if st[i] == st[i + 1]:
            st = np.delete(st, i + 1)
            st[i] *= 2
            st = np.append(st, 0)
    return st


def left(cop):
    for i in range(4):
        cop[i] = shift(cop[i])
    return cop


def right(cop):
    for i in range(4):
        cop[i] = shift(cop[i][::-1])
        cop[i] = np.flip(cop[i])
    return cop


def up(cop):
    cop = np.transpose(cop)
    cop = left(cop)
    return np.transpose(cop)


def down(cop):
    cop = np.transpose(cop)
    cop = right(cop)
    return np.transpose(cop)


# проверка возможности сдвига


def check(game, function):
    attempt = np.copy(game)
    function(attempt)
    if not np.array_equal(attempt, game):
        return 1
    else:
        return 0


# создаем тело игры
# Цикл игры (ход):
# 1. Программа проверяет возможность сдвига в одну из сторон
# 2. Игрок выбирает сторону сдвига, ячейки сдвигаются
# 3. При наличии пустого места, добавляется новая 2(4)
# 4. Отрисовывается новое состояние игрового поля

class MyGame(ar.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.score = 0
        self.death = 0
        self.game = game

    # создаем класс ячейки

    class Square:
        def __init__(self, x1, x2, y2, y1, color):
            self.x1 = x1
            self.x2 = x2
            self.y2 = y2
            self.y1 = y1
            self.color = color

        def draw(self):
            ar.draw_lrtb_rectangle_filled(self.x1, self.x2, self.y2,
                                          self.y1, self.color)

    def setup(self):
        ar.set_background_color(ar.color.LICORICE)

    # Управление Игрой:
    # "Space" - начать новую игру
    # "Escape" - выйти из игры
    # "Up" - совершить сдвиг вверх
    # "Down" - совершить сдвиг вниз
    # "Left" - совершить сдвиг влево
    # "Right" - совершить сдвиг вправо

    def on_key_press(self, key, modifiers):

        if key == ar.key.ESCAPE:
            ar.close_window()

        if key == ar.key.SPACE:
            self.game = insert(np.copy(start))
            self.score = 0
            self.death = 0

        if key == ar.key.LEFT:
            cop = np.copy(self.game)
            left(self.game)
            if not np.array_equal(cop, self.game):
                insert(self.game)

        if key == ar.key.RIGHT:
            cop = np.copy(self.game)
            right(self.game)
            if not np.array_equal(cop, self.game):
                insert(self.game)

        if key == ar.key.UP:
            cop = np.copy(self.game)
            up(self.game)
            if not np.array_equal(cop, self.game):
                insert(self.game)

        if key == ar.key.DOWN:
            cop = np.copy(self.game)
            down(self.game)
            if not np.array_equal(cop, self.game):
                insert(self.game)

    # проверяем возможность сдвига
    # нет возможности - проигрыш

    def on_update(self, delta_time):
        direct = 0
        direct += check(self.game, left)
        direct += check(self.game, right)
        direct += check(self.game, up)
        direct += check(self.game, down)
        if direct == 0:
            self.death = 1
        save(self.game)

    # отрисовка

    def on_draw(self):
        ar.start_render()
        ar.draw_lrtb_rectangle_filled(100, 500, 500, 100, colort)
        ar.draw_rectangle_filled(100, 300, 10, 410, colormt)
        ar.draw_rectangle_filled(200, 300, 10, 400, colormt)
        ar.draw_rectangle_filled(300, 300, 10, 400, colormt)
        ar.draw_rectangle_filled(400, 300, 10, 400, colormt)
        ar.draw_rectangle_filled(500, 300, 10, 410, colormt)
        ar.draw_rectangle_filled(300, 100, 400, 10, colormt)
        ar.draw_rectangle_filled(300, 200, 400, 10, colormt)
        ar.draw_rectangle_filled(300, 300, 400, 10, colormt)
        ar.draw_rectangle_filled(300, 400, 400, 10, colormt)
        ar.draw_rectangle_filled(300, 500, 400, 10, colormt)
        ar.draw_text("It's 2048 time", 150, 530, colorw, 24)
        self.score = np.max(self.game)
        x1 = 105
        y1 = 405
        x2 = 195
        y2 = 495
        for i in range(4):
            for j in range(4):
                if self.game[i][j]:
                    a = self.game[i][j]
                    color = d_color[a]
                    self.Square(x1, x2, y2, y1, color).draw()
                    text = str(a)
                    ar.draw_text(text, x1 + 10, y1 + 25,
                                 colorb, 24, align="center")
                x1 += 100
                x2 += 100
            x1 = 105
            x2 = 195
            y1 -= 100
            y2 -= 100
        if self.score == 2048:
            ar.draw_text("ВЫ ПОБЕДИЛИ!!!", 0, 250, colorw, 64)
        elif self.death == 1:
            ar.draw_text("ВЫ ПРОИГРАЛИ:/", 0, 250, colorw, 64)


# запускаем готовую игру. Enjoy!

twenty48 = MyGame(600, 600, "2048")
ar.finish_render()
ar.run()
