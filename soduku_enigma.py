#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/10/12 下午7:34
# @Author : Sui Chen
import random

import time
from reportlab.pdfgen import canvas

from soduku_generator import Soduku

CODE_LENGTH = 9
LENGTH = 3


class ColumnRow(object):
    def __init__(self):
        self._ordered_present = list()
        self.set = set()

    def add(self, a_number):
        self._ordered_present.append(a_number)
        self.set.add(a_number)

    def is_valid(self, second, third):
        testset = set()
        testset.update(self.set)
        testset.update(second.set)
        testset.update(third.set)
        return testset == set(range(CODE_LENGTH))

    def is_valid_two(self, other):
        return not self.set.intersection(other.set)

    def __str__(self):
        return ' '.join(map(lambda x: str(x+1), self._ordered_present))


class Face(object):
    def __init__(self, code=None):
        if code:
            self._code = code
        else:
            self._code = map(lambda x: x+1, range(CODE_LENGTH))
            random.shuffle(self._code)
        self.columns = list()
        self.rows = list()
        for i in range(LENGTH):
            row = ColumnRow()
            column = ColumnRow()
            for j in range(LENGTH):
                column.add(self._code[i + j * LENGTH])
                row.add(self._code[i * LENGTH + j])
            self.columns.append(column)
            self.rows.append(row)

    def render(self, canvas):
        canvas.saveState()
        empty_index = random.sample(range(9), 2)
        FONT_SIZE = 10
        GAP = 5
        for index, num in enumerate(self._code):
            x = index % 3 * (FONT_SIZE + GAP)
            y = index / 3 * (FONT_SIZE + GAP)
            if index not in empty_index:
                t = canvas.beginText(x, y)
                t.textLine(str(num))
                canvas.drawText(t)
        canvas.restoreState()

    def is_hori_valid(self, second, third):
        return all((self.rows[i].is_valid(second.rows[i], third.rows[i]) for i in range(LENGTH - 1)))

    def is_hori_valid_two(self, second):
        return all((self.rows[i].is_valid_two(second.rows[i]) for i in range(LENGTH - 1)))

    def is_verti_valid(self, second, third):
        return all((self.columns[i].is_valid(second.columns[i], third.columns[i]) for i in range(LENGTH - 1)))

    def is_verti_valid_two(self, second):
        return all((self.columns[i].is_valid_two(second.columns[i]) for i in range(LENGTH - 1)))

    def __str__(self):
        return '\n'.join(map(str, self.rows))


class AnswerFace(Face):
    def render(self, canvas):
        canvas.saveState()
        canvas.setFillColorRGB(1, 0, 0)
        super(AnswerFace, self).render(canvas)
        canvas.restoreState()


class TriFace(object):
    def __init__(self):
        self.faces = list()
        for i in range(3):
            self.faces.append(Face())

    def __str__(self):
        result = str()
        present_order = range(3)
        random.shuffle(present_order)
        for i in present_order:
            result += reduce(lambda x, y: x + '   ' + y, map(lambda x: str(x.rows[i]), self.faces))
            result += '\n'
        return result

    def has_valid(self, second, third):
        valid_result = list()
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    try:
                        if self.faces[i].is_hori_valid(second.faces[j], third.faces[k]):
                            valid_result.append((i, j, k))
                    except AttributeError:
                        if second is None:
                            raise AttributeError, 'second is None'
                        elif third is None:
                            raise AttributeError, 'third is None'
                        else:
                            raise AttributeError, 'self is None'
        return valid_result


class TriFaceWithOneKnownFace(TriFace):
    def __init__(self, known_face):
        super(TriFaceWithOneKnownFace, self).__init__()
        self.replace_face_index = random.randint(0, 2)
        self.faces[self.replace_face_index] = known_face

    @property
    def answer(self):
        return self.replace_face_index


class SodukuEnigma(object):
    def __init__(self):
        self.answer_position = [0, 0]
        self.answer_facelist = list()
        self.triface_list = [[None] * 9 for i in range(9)]
        self.get_valid_soduku()
        self.fill_rest()

    def get_valid_soduku(self):
        valid_soduku = Soduku()
        valid_soduku.fill()
        i_begin = random.randint(0, 6)
        j_begin = random.randint(0, 6)
        self.answer_position = [i_begin, j_begin]
        for i in range(3):
            for j in range(3):
                self.triface_list[i + i_begin][j + j_begin] =\
                    TriFaceWithOneKnownFace(AnswerFace(valid_soduku.get_subgrid_by_index(i * 3 + j).code))
                self.answer_facelist.append(self.triface_list[i + i_begin][j + j_begin].answer)

    def fill_rest(self):
        for row_index, row in enumerate(self.triface_list):
            for column_index, triface in enumerate(row):
                if triface is None:
                    while True:
                        new_triface = TriFace()
                        if self.check_invalid(row_index, column_index, new_triface):
                           self.triface_list[row_index][column_index] = new_triface
                           break

    def check_invalid(self, row_index, column_index, new_triface):
        check_list = [True, True, True]
        if column_index >= 2:
            check_list[0] = not new_triface.has_valid(self.triface_list[row_index][column_index - 2],
                                                      self.triface_list[row_index][column_index - 1])
        if column_index < 8 and self.triface_list[row_index][column_index + 1] is not None:
            if column_index != 0:
                check_list[1] = not new_triface.has_valid(self.triface_list[row_index][column_index + 1],
                                                          self.triface_list[row_index][column_index - 1])
            check_list[2] = not new_triface.has_valid(self.triface_list[row_index][column_index + 1],
                                                      self.triface_list[row_index][column_index + 2])
        return all(check_list)

    def render_self(self):
        SIDE = 40
        GAP = 10
        PAGE_SIDE = 10.5 * (SIDE + GAP)
        c = canvas.Canvas('soduku_enigma.pdf', bottomup=False)
        for face_index in range(3):
            # c = canvas.Canvas('soduku_enigma_%s.pdf' % time.strftime('%H:%M:%S', time.localtime()), bottomup=False)
            c.setPageSize((PAGE_SIDE, PAGE_SIDE))
            y = 0
            for row in self.triface_list:
                c.translate(0, SIDE + GAP)
                c.saveState()
                for triface in row:
                    c.translate(SIDE + GAP, 0)
                    triface.faces[face_index].render(c)
                c.restoreState()
            c.showPage()
        c.save()


if __name__ == '__main__':
    a = SodukuEnigma()
    a.render_self()
    print a.answer_position
    print a.answer_facelist
