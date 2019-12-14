import operator
import random
from collections import Counter
from copy import deepcopy
from functools import reduce
from math import factorial

import numpy as np
import itertools

## sprawdza czy są wszystkie cyfry
def all_set(s):
    set = '01234678'
    return 0 not in [c in s for c in set]

## przyjmuje input w postaci stringa i sprawdza czy jest poprawny
def input_string():
    print('Podaj tablicę w formacie cyfr od 0 do 8 np. 012345678')
    string = input()

    if len(string) != 9 or all_set(string) == 0:
        print('Wprowadzono niepoprawne dane')
        print('Koniec programu')
        return

    return string

## podany string przekształca w planszę
def make_board(s):
    board = np.array(list(map(int, s)))
    return board

## oblicza liczbę inwersji, żeby sprawdzić czy uda sie ułożyć -> podzielna przez 2 = da się
def count_inversions(board):
    inversions = 0
    k = board[board != 0]
    for i in range(len(k) - 1):
        t = np.array(np.where(k[i + 1:] < k[i])).reshape(-1)
        inversions += len(t)
    return inversions

## sprawdza czy liczba inwersji jest parzysta
def check_if_solvable(board):
    if count_inversions(board) % 2 != 0:
        return False
    return True

## generate all puzzles possible
def generate_puzzles():
    puzzle_permutations = np.array(list(itertools.permutations([1, 2, 3, 4, 5, 6, 7, 8, 0])))
    print(puzzle_permutations)
    return puzzle_permutations

## delete 123456780 from permutations
def delete_goal_permutation(permutations):
    puzzle_permutations = np.delete(permutations, 0, 0)
    print(puzzle_permutations)
    return puzzle_permutations

## delete non solvable permutations
def delete_non_solvable(puzzles):
    perm_number = int(int(puzzles.size)/9)
    p = np.array(list())
    for i in range(int(perm_number)):
        if not check_if_solvable(puzzles[i]):
            p = np.delete(puzzles, i, 0)
    return p

## pick random 10 puzzles
def pick_random_puzzles(puzzles):
    random_indexes = [random.randint(0, int(int(puzzles.size)/9)) for x in range(10000)]
    puzzles_selected = np.array(list())
    for i in range(int(int(puzzles.size)/9)):
        if i in random_indexes:
            puzzles_selected = np.append(puzzles_selected, puzzles[i], 0)
    print(int(int(puzzles_selected.size)/9))
    puzzles_solvable = delete_non_solvable(puzzles_selected)
    return puzzles_solvable

## Przyporządkuj współrzędne dla puzli
def assign_coordinates(b):
    coordinates = np.array(range(9))
    for x, y in enumerate(b):
        coordinates[y] = x
    return coordinates

## oblicz manhattan distance
def manhattan_distance_calculator(coor_b, coor_g):
    # In a plane with p1 at (x1, y1) and p2 at (x2, y2), it is |x1 - x2| + |y1 - y2|.
    mhd = abs(coor_b // 3 - coor_g // 3) + abs(coor_b % 3 - coor_g % 3)
    return sum(mhd[1:])

## rozwiązanie
def solve(b, g):
    # można przesuwać 0 w górę, dół, lewo i prawo -> konieczne współrzędne 0

    moves = np.array([('u', [0, 1, 2], -3),
                      ('d', [6, 7, 8], 3),
                      ('l', [0, 3, 6], -1),
                      ('r', [2, 5, 8], 1)],
                     dtype=[('move', str, 1),
                            ('pos', list),
                            ('delta', int)])

    board_state = [('board', list),
                   ('parent', int),
                   ('gn', int), #poziom w drzewie
                   ('hn', int) #odległość od celu
                   ]
    # inicjalizacja kolejki priorytetów
    board_priority = [('pos', int),
                  ('fn', int)
                  ]

    coordinates_board = assign_coordinates(b)
    coordinates_goal = assign_coordinates(g)

    # początkowe wartości
    hn = manhattan_distance_calculator(coordinates_board, coordinates_goal)
    parent = -1
    gn = 0
    current_state = np.array([(b, parent, gn, hn)], board_state)
    priority = np.array([(0, hn)], board_priority)

    while True:
        priority = np.sort(priority, kind='mergesort', order=['fn', 'pos']) #sort priority queue
        pos, fn = priority[0] #pick up first to explore
        priority = np.delete(priority, 0, 0) #remove from queue
        b, parent, gn, hn = current_state[pos]
        b = np.array(b)
        loc = int(np.where(b ==0)[0])
        gn = gn + 1 #increase level g(n) by 1

        for m in moves:
            if loc not in m['pos']:
                succ = deepcopy(b)
                succ[loc], succ[loc + m['delta']] = succ[loc + m['delta']], succ[loc] # do the move
                if ~(np.all(list(current_state['board']) == succ, 1)).any():
                    hn = manhattan_distance_calculator(assign_coordinates(succ), coordinates_goal)
                    q = np.array([(succ, pos, gn, hn)], board_state) #generate and add new state in the list
                    current_state = np.append(current_state, q, 0)
                    fn = gn + hn #calculate f(n)
                    q = np.array([(len(current_state) - 1, fn)], board_priority) #add to priority queue
                    priority = np.append(priority, q, 0)
                    if np.array_equal(succ, g):
                        print('Koniec układania!')
                        return current_state, len(priority)

## output
def genoptimal(state):
    optimal = np.array([], int).reshape(-1, 9)
    last = len(state) - 1
    while last != -1:
        optimal = np.insert(optimal, 0, state[last]['board'], 0)
        last = int(state[last]['parent'])
    return optimal.reshape(-1, 3, 3)


####################################
def main():
    print()
    # zapisujemy do zmiennej ułożenie
    goal = np.array([1, 2, 3, 4, 5, 6, 7, 8, 0])
    print('Czy chcesz sam wpisać tablicę?')
    print('1. TAK')
    print('2. NIE')
    print('3. Chcę popatrzeć na układanie')
    opcja = input('Wybrana opcja: ')
    if opcja != '1' and opcja != '2' and opcja != '3':
        print('Podane opcje nie mieszczą się w zakresie.')
        print('Koniec programu.')
        return
    elif opcja == '1':
        string = input_string()
        board = make_board(string)
        print(board)
        if check_if_solvable(board):
            print('Tą tablicę da się ułożyć. Zaczynamy :D')
            state, explored = solve(board, goal)
            print('Wygenerowanych rozwiązań: ', len(state))
            print('Przeszukanych: ', len(state) - explored)
            optimal = genoptimal(state)
            print('Wygenerowano zoptymalizowanych kroków: ', len(optimal) - 1)
            print(optimal)
            return
        print('Tej tablicy nie da się ułożyć.')
        print('Koniec programu')
        return
    elif opcja == '2':
        print('Tworzymy wszystkie możliwe tablice:')
        puzzles = generate_puzzles()
        print('Liczba stworzonych tablic: ', int(int(puzzles.size)/9))
        print('Usuwamy z tablic opcję 123456780.')
        puzzles_without_goal = delete_goal_permutation(puzzles)
        print('Losujemy 10000 układanek z', len(puzzles_without_goal))
        puzzles_solvable_random = pick_random_puzzles(puzzles_without_goal)
        if int(len(puzzles_solvable_random)) == 0:
            print('Wśród 10000 układanek nie trafiła się ani jedna szczęśliwa.')
            print('Koniec programu')
            return
        for i in range(int(int(puzzles_solvable_random.size)/9)):
            state, explored = solve(puzzles_solvable_random[i], goal)
            print('Wygenerowanych rozwiązań: ', len(state))
            print('Przeszukanych: ', len(state) - explored)
            optimal = genoptimal(state)
            print('Wygenerowano zoptymalizowanych kroków: ', len(optimal) - 1)
            print(optimal)
        return
    elif opcja == '3':
        string = '182043765'
        board = make_board(string)
        print(board)
        if check_if_solvable(board):
            print('Tą tablicę da się ułożyć. Zaczynamy :D')
            state, explored = solve(board, goal)
            print('Wygenerowanych rozwiązań: ', len(state))
            print('Przeszukanych: ', len(state) - explored)
            print('Manhattan distance: ', state['hn'])
            optimal = genoptimal(state)
            print('Wygenerowano zoptymalizowanych kroków: ', len(optimal) - 1)
            print(optimal)
            return
        print('Tej tablicy nie da się ułożyć.')
        print('Koniec programu')
        return


####################################

if __name__ == '__main__':
    main()
