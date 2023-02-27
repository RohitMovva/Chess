import tkinter as tk
from tkinter import messagebox
import io
import cairosvg
import os
from PIL import Image, ImageTk


class chessPiece(tk.Button):
    def __init__(self, master, color, coord, piece, piece_info):
        tk_image = tk.PhotoImage(width=1, height=1)
        self.piece_info = piece_info
        self.has_piece = False
        self.has_moved = False
        self.promoter = [False, []]
        if piece != None:
            tk_image = piece
            self.has_piece = True

        tk.Button.__init__(self, master, image=tk_image, height=150, width=150, text='', bg=color,
                           font=('Arial', 24), highlightthickness=0, activebackground="#FCE6CE", borderwidth=0)
        self.bind('<Button-1>', self.onclick)
        self.image = tk_image
        self.color = color
        self.coord = coord

    def onclick(self, filler):
        self.master.handle_click(self)

    def remove_piece(self):
        self.has_piece = False
        self['bg'] = self.color
        self['image'] = self.image = tk.PhotoImage(width=1, height=1)
        self.piece_info[0] = None
        self.piece_info[1] = None

    def add_piece(self, piece, piece_info):
        self.has_moved = True
        self.has_piece = True
        self['image'] = self.image = piece
        self.piece_info[0] = piece_info[0]
        self.piece_info[1] = piece_info[1]

    def highlight(self):
        self['width'] -= 16
        self['height'] -= 16
        # uncomment for buttons to have a different border when selected
        self['borderwidth'] = 8

    def unhighlight(self):
        self['width'] = 150
        self['height'] = 150
        # uncomment for buttons to have a different border when selected
        self['borderwidth'] = 0

    def end(self):
        self.unbind('<Button-1>')
        self['activebackground'] = self.color

    def unend(self):
        self.bind('<Button-1>', self.onclick)
        self['activebackground'] = "#FCE6CE"

    def promotion_option(self, image, promoter):
        self.promoter = promoter
        self['image'] = image

    def become_normal(self):
        self.promoter = [False, None]
        self['image'] = self.image


class chessBoard(tk.Frame):
    def __init__(self, master):
        self.selected_square = None
        piecemap = {}
        step = 0
        pawns = []
        cwd = os.getcwd()
        counter = 0
        self.turn = True
        self.piece_type_dict = {0: 'r', 1: 'n', 2: 'b', 3: 'q', 4: 'k'}
        self.value_dict = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0, None: 0}
        self.promote_to_piece = [[], []]
        with os.scandir('pieces/') as pieces:
            for old_piece in pieces:
                image_data = cairosvg.svg2png(url=cwd + "/pieces/" + old_piece.name)
                image = Image.open(io.BytesIO(image_data))
                resized = image.resize((150, 150))
                piece = ImageTk.PhotoImage(resized, master=master)
                if counter > 1:
                    counter = 0
                    step += 1
                if old_piece.name == 'Chess_pub45.svg' or old_piece.name == 'Chess_puw45.svg':
                    pawns.append(piece)
                    continue
                piecemap[(counter * 7, 0 + step)] = piece
                if "royal" not in old_piece.name:
                    piecemap[(counter * 7, 7 - step)] = piece
                if counter == 0 and step < 4:
                    self.promote_to_piece[0].append(piece)
                elif step < 4:
                    self.promote_to_piece[1].append(piece)
                counter += 1

        for i in range(0, len(pawns)):
            for j in range(0, 8):
                piecemap[5 * i + 1, j] = pawns[i]

        self.board = []
        self.highlighted_squares = []
        tk.Frame.__init__(self, master, bg='black')
        self.score = None
        self.player_labels = [[], []]
        for i in range(0, 2):
            currframe = tk.Frame(master, height=5, width=50)
            self.player_labels[i].append(currframe)
            self.player_labels[i].append(tk.Label(currframe, text=("Player " + str(i+1)), height=5, width=10, bg='black', fg='white'))
            self.player_labels[i].append(tk.Label(currframe, text="Score: " + str(self.calculate_score(bool(i))), height=5, width=10, bg='black', fg='white'))
            self.player_labels[i].append(tk.Label(currframe, text="Relative Score: " +
                    str(self.calculate_score(bool(i))-self.calculate_score(not bool(i))), height=5, width=20, bg='black', fg='white'))
            # str(self.calculate_score(bool(i))-self.calculate_score(not bool(i))
        self.player_labels[1][0].grid(row=0, column=0, columnspan=8)
        for i in range(1, len(self.player_labels[0])):
            self.player_labels[1][i].grid(row=0, column=i)
        self.grid()
        self.rowconfigure(9, minsize=1)
        self.chessFrame = tk.Frame(self, bg='white')
        self.chessFrame.grid(row=8, column=0, columnspan=8)
        self.kings = []
        self.promoting_options = []
        self.past_move = []
        for i in range(0, 8):
            self.board.append([])
            for j in range(0, 8):
                piece_info = [None, None]
                if i == 0 or i == 7:
                    col = j
                    if col > 4:
                        col = 7 - col
                    piece_info[1] = self.piece_type_dict.get(col, None)
                if i == 1 or i == 6:
                    piece_info[1] = 'p'

                if piece_info[1] != None:
                    piece_info[0] = False
                    if i > 4:
                        piece_info[0] = True
                if (i + j) % 2 == 0:
                    self.board[i].append(chessPiece(self, "#F0D9B5", (i, j), piecemap.get((i, j), None), piece_info))
                else:
                    self.board[i].append(chessPiece(self, "#B58863", (i, j), piecemap.get((i, j), None), piece_info))

                if piece_info[1] == 'k' and piece_info[0] == True:
                    self.kings.append(self.board[i][j])
                elif piece_info[1] == 'k' and piece_info[0] == False:
                    self.kings.append(self.board[i][j])
                self.board[i][j].grid(row=i+1, column=j, sticky='wnes')
        self.player_labels[0][0].grid(row=8, column=0, columnspan=8)
        for i in range(1, len(self.player_labels[0])):
            self.player_labels[0][i].grid(row=0, column=i)
        for i in range(0, len(self.player_labels)):
            self.player_labels[i][2]['text'] = "Score: " + str(self.calculate_score(bool(i)))
            self.player_labels[i][3]['text'] = "Relative Score: " + str(self.calculate_score(bool(i)) - self.calculate_score(not bool(i)))

    def calculate_score(self, player):
        score = 0
        for i in self.board:
            for j in i:
                if j.piece_info[0] == player:
                    score += self.value_dict[j.piece_info[1]]
        return score

    def handle_click(self, square):
        # promote a piece
        if square.promoter[0]:
            for i in self.board:
                for j in i:
                    j.unend()
            self.past_move[1].remove_piece()
            self.past_move[1].add_piece(square["image"], square.promoter[1])
            for i in self.promoting_options:
                i.become_normal()
            self.promoting_options = []
            self.switch_board(square)

        # select a square
        elif square.has_piece and self.turn == square.piece_info[0] and square != self.selected_square:
            for i in self.highlighted_squares:
                i.unhighlight()
            self.selected_square = square
            self.highlighted_squares = self.generate_moves_for_square(square, square.piece_info, False)
            # deleting pieces before this point
            for i in self.highlighted_squares:
                i.highlight()

        # move a piece
        elif self.selected_square != None and square != self.selected_square and square in self.highlighted_squares:
            for i in self.highlighted_squares:
                i.unhighlight()
            if self.selected_square.piece_info[1] == 'p' and self.selected_square.coord[1] - square.coord[1] in [1, -1] and not square.has_piece:
                self.en_passant(square)
            elif self.selected_square.piece_info[1] == 'k' and square.coord[1] - self.selected_square.coord[1] in [-2, 2]:
                self.castle(square)
            else:
                self.shift_piece(square, self.selected_square)
            self.past_move = [self.selected_square, square]

            if square.piece_info[1] == 'p' and ((square.piece_info[0] and square.coord[0] == 0) or (
                    not square.piece_info[0] and square.coord[0] == 7)):
                self.promote_piece(square, square.coord[1])
                return
            self.switch_board(square)

    def shift_piece(self, p1, p2):
        temp = [(p1.image, p1.piece_info[:], p1.has_moved), (p2.image, p2.piece_info[:], p2.has_moved)]
        if p2.piece_info[1] == 'k':
            self.kings[int(p2.piece_info[0])] = p1
        p1.remove_piece()
        p2.remove_piece()
        p1.add_piece(temp[1][0], temp[1][1])
        return temp

    def promote_piece(self, piece, column):
        start = 1
        end = 5
        if piece.coord[0] == 7:
            start = 6
            end = 2
        for i in self.board:
            for j in i:
                j.end()
        counter = 0
        for i in range(start, end, int((start - end) / -4)):
            self.board[i][column].unend()
            self.promoting_options.append(self.board[i][column])
            self.board[i][column].promotion_option(self.promote_to_piece[int(piece.piece_info[0])][counter],
                                                   [True, [self.turn, self.piece_type_dict[counter]]])
            counter += 1

    def castle(self, square):
        if square.coord[1] == 6:
            square = self.board[square.coord[0]][square.coord[1] + 1]
        else:
            square = self.board[square.coord[0]][square.coord[1] - 1]
        temp = [(self.kings[self.turn].image, self.kings[self.turn].piece_info[:]),
                (square.image, square.piece_info[:])]
        self.kings[self.turn].remove_piece()
        square.remove_piece()
        switches = [6, 5]
        if square.coord[1] == 0:
            switches[0] = 2
            switches[1] = 3
        self.board[int(self.turn) * 7][switches[0]].add_piece(temp[0][0], temp[0][1])
        self.board[int(self.turn) * 7][switches[1]].add_piece(temp[1][0], temp[1][1])
        self.kings[self.turn] = self.board[int(self.turn) * 7][switches[0]]

    def en_passant(self, square):
        self.past_move[1].remove_piece()
        square.add_piece(self.selected_square.image, self.selected_square.piece_info[:])
        self.selected_square.remove_piece()

    def switch_board(self, square):
        if square.piece_info[1] == 'k' and square.piece_info[0]:
            self.kings[0] = square
        elif square.piece_info[1] == 'k' and not square.piece_info[0]:
            self.kings[1] = square
        self.turn = not self.turn
        self.selected_square = None

        self.player_labels[0][0].grid(row=8*int(self.turn), column=0, columnspan=8)
        self.player_labels[1][0].grid(row=8*int(not self.turn), column=0, columnspan=8)

        for i in range(0, 8):
            for j in range(0, 8):
                if not self.turn:
                    self.board[i][j].grid(row=8 - i, column=j)
                else:
                    self.board[i][j].grid(row=i+1, column=j)

        for i in range(0, 2):
            self.player_labels[i][2]['text'] = "Score: " + str(self.calculate_score(not bool(i)))
            self.player_labels[i][3]['text'] = "Relative Score: " + str(self.calculate_score(not bool(i)) - self.calculate_score(bool(i)))

        for i in self.kings:
            i['bg'] = i.color
        if self.check_for_check():
            self.kings[int(self.turn)]['bg'] = 'red'

        self.check_for_end()


    def do_checks(self, coord, s, take):
        if not 0 <= coord[0] <= 7 or not 0 <= coord[1] <= 7:
            return False
        piece = self.board[coord[0]][coord[1]]
        if take == 0 and piece.has_piece:
            return False
        elif take == 1 and not piece.has_piece:
            return False
        if piece.piece_info[0] == self.turn:
            return False
        if not s and not self.is_valid(piece):
            return False
        return True

    def generate_moves_for_square(self, square, piece_info, s):
        moves = []
        x = square.coord[0]
        y = square.coord[1]
        if piece_info[1] == 'p':  # pawn
            direction = -1
            # yeah, I hardcoded this bit cope
            if not piece_info[0]:
                direction = 1
            if self.do_checks((x + direction, y), s, 0):
                moves.append(self.board[x + direction][y])
                if ((piece_info[0] and square.coord[0] == 6) or (not piece_info[0] and square.coord[0] == 1)) \
                        and self.do_checks((x + 2 * direction, y), s, 0):
                    moves.append(self.board[x + 2 * direction][y])

            if self.do_checks((x + direction, y + 1), s, 1):
                moves.append(self.board[x + direction][y + 1])
            if self.do_checks((x + direction, y - 1), s, 1):
                moves.append(self.board[x + direction][y - 1])
            if self.past_move != [] and self.past_move[1].piece_info[1] == 'p' and self.past_move[0].coord[0] - self.past_move[1].coord[0] in [2, -2] and \
                    self.past_move[1].coord[1]-square.coord[1] in [-1, 1] and self.past_move[1].coord[0] == square.coord[0]:
                moves.append(self.board[x + direction][self.past_move[1].coord[1]])

        if piece_info[1] == 'r' or piece_info[1] == 'q':  # rook + queen
            shifts = [0, 0]
            for i in [(1, 0), (-1, 0), (1, 1), (-1, 1)]:
                shifts[i[1]] += i[0]
                while self.do_checks((x + shifts[0], y + shifts[1]), s, -1):
                    if self.do_checks((x + shifts[0], y + shifts[1]), s, 1):
                        moves.append(self.board[x + shifts[0]][y + shifts[1]])
                        break
                    elif self.do_checks((x + shifts[0], y + shifts[1]), s, 0):
                        moves.append(self.board[x + shifts[0]][y + shifts[1]])
                    shifts[i[1]] += i[0]
                shifts[0] = shifts[1] = 0

        if piece_info[1] == 'b' or piece_info[1] == 'q':  # bishop + queen
            shifts = [0, 0]
            for i in [-1, 1]:
                for j in [-1, 1]:
                    shifts[0] += i
                    shifts[1] += j
                    while self.do_checks((x + shifts[0], y + shifts[1]), s, -1):
                        if self.do_checks((x + shifts[0], y + shifts[1]), s, 1):
                            moves.append(self.board[x + shifts[0]][y + shifts[1]])
                            break
                        elif self.do_checks((x + shifts[0], y + shifts[1]), s, 0):
                            moves.append(self.board[x + shifts[0]][y + shifts[1]])
                        shifts[0] += i
                        shifts[1] += j
                    shifts[0] = shifts[1] = 0

        if piece_info[1] == 'n':  # knight
            for i in [-2, 2]:
                for j in [-1, 1]:
                    if self.do_checks((x + i, y + j), s, -1):
                        moves.append(self.board[x + i][y + j])
                    if self.do_checks((x + j, y + i), s, -1):
                        moves.append(self.board[x + j][y + i])

        if piece_info[1] == 'k':  # king
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i == 0 and j == 0:
                        continue
                    if self.do_checks((x + i, y + j), s, -1):
                        moves.append(self.board[x + i][y + j])

            for i in [(1, 2), (-1, -2, -3)]:
                if square.has_moved or self.board[square.coord[0]][-7 * (len(i) - 2) + 7].has_moved:
                    continue
                for j in i:  # [(1, 2), (-1, -2, -3)]
                    if not self.do_checks((x, y + j), s, 0):
                        break
                    if j == i[len(i) - 1]:
                        moves.append(self.board[x][y + j])

        return moves

    def is_valid(self, square):
        temp = self.shift_piece(square, self.selected_square)
        if self.check_for_check():
            self.redo(temp, square)
            return False
        self.redo(temp, square)
        return True

    def redo(self, temp, square):
        if temp[1][1][1] == 'k':
            self.kings[temp[1][1][0]] = self.selected_square
        self.selected_square.add_piece(temp[1][0], temp[1][1])
        self.selected_square.has_moved = temp[1][2]
        square.remove_piece()
        square.has_moved = temp[0][2]
        if temp[0][1][0] != None:
            square.add_piece(temp[0][0], temp[0][1])

    def check_for_check(self):
        self.turn = not self.turn
        for i in self.board:
            for j in i:
                if j.piece_info[0] == self.turn:
                    for k in self.generate_moves_for_square(j, j.piece_info, True):
                        if k.coord == self.kings[not self.turn].coord:
                            self.turn = not self.turn
                            return True
        self.turn = not self.turn
        return False

    def check_for_end(self):
        for i in self.board:
            for j in i:
                if j.piece_info[0] == self.turn:
                    self.selected_square = j
                    if self.generate_moves_for_square(j, j.piece_info, False):
                        self.selected_square = None
                        return

        self.selected_square = None
        if self.check_for_check():
            self.end_game(not self.turn)
        else:
            self.end_game(None)

    def end_game(self, winner):
        for i in self.board:
            for j in i:
                j.end()

        if winner == None:
            tk.messagebox.showinfo(title="Game Over!", message="Stalemate!")
        else:
            tk.messagebox.showinfo(title="Game Over!", message="Congratulations Player " + str(int(self.turn)+1) + " you won!")


def chessGrid():
    root = tk.Tk()
    root.title('Chess')
    root.configure(background='black')
    game = chessBoard(root)
    root.mainloop()


chessGrid()
