#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/10/13 下午8:44
# @Author : Sui Chen
import random


class Subgrid(set):
    def __init__(self, iterable=list()):
        super(Subgrid, self).__init__(iterable)
        self.code = list()

    def add(self, single_number):
        super(Subgrid, self).add(single_number)
        self.code.append(single_number)

    def update(self, a_list):
        super(Subgrid, self).update(a_list)
        self.code.extend(a_list)

    def __str__(self):
        result = str()
        for index, num in enumerate(self.code):
            result += str(num) + ' '
            if index % 3 == 2:
                result += '\n'
        return result


class BigColumn(object):
    def __init__(self, code):
        self.code = code

    def __str__(self):
        result = str()
        for index, num in enumerate(self.code):
            result += str(num) + ' '
            if index % 3 == 2:
                result += '\n'
            if index % 9 == 8:
                result += '\n'
        return result


class BigRow(object):
    def __init__(self, code):
        self.code = code

    def __str__(self):
        result = str()
        for index, code in enumerate(self.code):
            result += str(code) + ' '
            if index % 3 == 2 and index % 9 != 8:
                result += '  '
            elif index % 9 == 8:
                result += '\n'
        return result


class Soduku(object):
    def __init__(self):
        self._code = [0] * 9 * 9
        self.repository_list = list()

    def fill(self, index=0):
        valid_repository = self.get_valid_repository(index)
        if valid_repository:
            num = random.sample(valid_repository, 1)[0]
            self.repository_list[index].remove(num)
            self.set_number(index, num)
            if index < 80:
                self.fill(index + 1)
        else:
            self.set_number(index, 0)
            self.repository_list.pop()
            self.fill(index - 1)

    def position(self, index):
        return index % 9, index / 9

    def get(self, index):
        return self._code[index]

    def set_number(self, index, number):
        self._code[index] = number

    def get_subgrid(self, i, j):
        row = j / 3 * 3
        column = i / 3 * 3
        subgrid = Subgrid()
        for index in range(3):
            subgrid.update(self._code[(row + index) * 9 + column: (row + index) * 9 + column + 3])
        return subgrid

    def get_subgrid_by_index(self, index):
        row = index / 3 * 3
        column = index % 3 * 3
        subgrid = Subgrid()
        for index in range(3):
            subgrid.update(self._code[(row + index) * 9 + column: (row + index) * 9 + column + 3])
        return subgrid

    def get_row(self, num):
        return set(self._code[num * 9: (num + 1) * 9])

    def get_column(self, num):
        return set(self._code[num + x * 9] for x in range(9))

    def get_valid_repository(self, index):
        try:
            return self.repository_list[index]
        except IndexError:
            i, j = self.position(index)
            total = {1, 2, 3, 4, 5, 6, 7, 8, 9}
            row = self.get_row(j)
            column = self.get_column(i)
            subgrid = self.get_subgrid(i, j)
            rest = total - row - column - subgrid
            if self.get(index) != 0:
                rest.add(self.get(index))
            self.repository_list.append(rest)
            return rest

    def completed(self):
        return all(map(lambda x: x != 0, self._code))

    def get_big_row(self, index):
        code = self._code[index * 27: (index + 1) * 27]
        return BigRow(code)

    def get_big_column(self, index):
        code = list()
        for i in range(9):
            code.extend(self._code[index * 3 + i * 9: (index + 1) * 3 + i * 9])
        return BigColumn(code)

    def __str__(self):
        result = str()
        for index, code in enumerate(self._code):
            result += str(code) + ' '
            if index % 3 == 2 and index % 9 != 8:
                result += '  '
            elif index % 9 == 8 and index % 27 != 26:
                result += '\n'
            elif index % 27 == 26:
                result += '\n\n'
        return result


if __name__ == '__main__':
    a = Soduku()
    a.fill()
    print a
    print a.get_big_row(0)
    print a.get_big_column(0)
    print a.get_subgrid_by_index(8)
