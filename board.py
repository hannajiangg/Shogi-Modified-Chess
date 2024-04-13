import os
import sys
import copy

class Board:
    """
    Class that represents the BoxShogi board
    """
    # The BoxShogi board is 5x5
    BOARD_SIZE = 5
    # MOVE: Move (move, a1, b1)
    # move_state: List of moves for -f
    # initial_state: Initial board
    # TURNS: Rounds/turns played
    # PIECETYPE: 'drop' piece getting dropped in proper cap (drop, THIS, a1)
    # PIECETYPE: 'move' piece getting moved in proper cap (move, a1, a2) piece from a1 on the board
    # POSITION: 'drop' end location and 'move' end location of piece respectively
    # INTEARACTIVE: -f or -i
    def __init__(self, move, move_state, initial_state, upper_cap, lower_cap, illegal_tuple, turn, last_move, piece_type, position, interactive=None):
        self._board = self._initEmptyBoard()
        self.move = move
        self.move_state = move_state
        self.initial_state = initial_state
        self.upper_cap = upper_cap
        self.lower_cap = lower_cap
        self.illegal_tuple = illegal_tuple
        self.turn = turn
        self.last_move = last_move
        self.piece_type = piece_type
        self.position = position
        self.interactive = interactive

        # ALLPIECES: Pieces on the board in [(0, 0, 'd')] format
        # DIRECTIONS: Directions the piece in play can move
        self.all_pieces = self.get_pieces()
        self.directions = None

        # KING: King in check danger, uppercase or lowercase d
        # KINGCOORD: King coordinates in (0, 0) form
        # KINGLETTER: King coordiantes in a1 form
        self.king = self.determine_king()

        self.king_coord = None
        self.king_letter = None

    def _initEmptyBoard(self):
        empty_board = [['__' for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        return empty_board
    def __repr__(self):
        return self._stringifyBoard()
    def _stringifyBoard(self):
        """
        Utility function for printing the board
        """
        s = ''
        for row in range(len(self._board) - 1, -1, -1):

            s += '' + str(row + 1) + ' |'
            for col in range(0, len(self._board[row])):
                s += self._stringifySquare(self._board[col][row])

            s += os.linesep

        s += '    a  b  c  d  e' + os.linesep
        return s
    def _stringifySquare(self, sq):
        """
       	Utility function for stringifying an individual square on the board

        :param sq: Array of strings.
        """
        if type(sq) is not str or len(sq) > 2:
            raise ValueError('Board must be an array of strings like "", "P", or "+P"')
        if len(sq) == 0:
            return '__|'
        if len(sq) == 1:
            return ' ' + sq + '|'
        if len(sq) == 2:
            return sq + '|'
    # Input position a1 to return board row and column 0, 0
    def board_coordinates(self, position):
        row = ord(position[0]) - ord('a')
        col = int(position[1]) - 1
        return row, col
    # Input coordinate 0, 0 to return position a1
    def coordinates_to_letter(self, row, col):
        row_letter = chr(ord('a') + row)
        col_number = col+ 1
        return row_letter + str(col_number)
    # Iniital console output asking player for move in interactive mode
    def start_output_interactive(self):
        self.initial_state = self.init_interactive_pieces()
        self.init_board()
        print(self.__str__())
        self.report_end_capture()
        print()
        move = input('lower>')
        return move
    # Initialize board for file mode by placing pieces on board
    def init_board(self):
        for piece_info in self.initial_state:
            p_piece = piece_info['piece']
            p_position = piece_info['position']
            row, col, = self.board_coordinates(p_position)
            self._board[row][col] = p_piece
    # Dynamically gets pieces [{'piece': 'S', 'position': 'd5'}]
    def init_interactive_pieces(self):
        i_pieces = []
        n = self.BOARD_SIZE 
        col_left = [chr(ord('a') + i) + '1' for i in range(n)]
        col_top = [chr(ord('a') + i) + str(n) for i in range(n)]
        label = ['d', 's', 'r', 'g', 'n', 'p']
        for i, position in enumerate(col_left):
            piece_name = label[i % len(label)]
            if i == 0:
                i_pieces.append({'piece': label[-1], 'position': chr(ord(position[0])) + str(int(position[1])+1)})
                col_top_below = [chr(ord('a') + i) + str(n - 1) for i in range(n)]
                i_pieces.append({'piece': label[-1].upper(), 'position': col_top_below[n - i - 1]})
            i_pieces.append({'piece': piece_name, 'position': position})
            i_pieces.append({'piece': piece_name.upper(), 'position': col_top[n- i - 1]})
        return i_pieces
    # Determines who the winner is based on the piece type in move
    def upper_winner(self, piece, truth):
        return 'lower' if piece.isupper() else 'UPPER' if truth else 'lower' if piece.islower() else 'UPPER'
    # Retrieves piece from a coordinate of the board
    def get_piece(self, start_position):
        row, col, = self.board_coordinates(start_position)
        piece = self._board[row][col]
        return piece
    # Removes piece from letter representation like a1 on the board
    def remove_piece(self, start_position):
        row, col, = self.board_coordinates(start_position)
        self._board[row][col] = '__'
    # Adds piece from coordinates like 0, 0
    def add_piece(self):
        end_row, end_col, = self.board_coordinates(self.position)
        potential_piece = self._board[end_row][end_col]
        if potential_piece == '__':
            self._board[end_row][end_col] = self.piece_type
            return 1
        elif potential_piece.isupper() != self.piece_type.isupper():
            self._board[end_row][end_col] = self.piece_type
            return potential_piece.replace('+', '')
        return 1
    # Helper to piece promote, validates if piece in promotion zone case sensitive
    def promotion_zone(self, piece, coord):
        _, col = self.board_coordinates(coord)
        if piece.islower():
            return col == self.BOARD_SIZE - 1
        return col == 0
    # CASE: Normal promotion
    def piece_promote(self, piece, start_coord):
        promoted_pieces = {
        'r': '+r', 'R': '+R',
        'g': '+g', 'G': '+G',
        'n': '+n', 'N': '+N',
        'p': '+p', 'P': '+P'
        }
        promoted = piece
        # Validate piece start or end in promotion zone
        if piece in promoted_pieces and (self.promotion_zone(piece, start_coord) or self.promotion_zone(piece, self.position)):
            promoted =  promoted_pieces[piece]
            return promoted
        elif piece.lower() not in promoted_pieces:
            return False     
    # Determines player turn, based on how many turns have been played
    def determine_turn(self, start_piece):
        self.piece_type = start_piece.upper()if self.turn % 2 == 1 else start_piece.lower()
    # Moves for each piece
    def get_piece_moves(self, lower_label):
        # Static to piece
        dir = []
        if lower_label == 'd':
            dir.append([(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)])
        elif lower_label == 's':
            dir.append([(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1)])
        elif lower_label == 'r':
            dir.append([(0, 1), (1, -1), (1, 1), (-1, -1), (-1, 1)])
        elif lower_label == 'p':
            dir.append([(0, 1)])
        # Dynamic across board
        if lower_label == 'n':
            dir.append([(1, 0), (-1, 0), (0, 1), (0, -1)])
        elif lower_label == 'g':
            dir.append([(1, 1), (-1, -1), (-1, 1), (1, -1)])
        # For promoted, taken from the above
        if lower_label == '+r':
            # Shield, static
            dir.append([(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1)])
        elif lower_label == '+g':
            # Governance (dynamic) + Drive (static)
            dir.append([(1, 1), (-1, -1), (-1, 1), (1, -1)])
            dir.append([(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)])
        elif lower_label == '+n':
            # Notes (dynamic) + Drive (static)
            dir.append([(1, 0), (-1, 0), (0, 1), (0, -1)])
            dir.append([(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)])
        elif lower_label == '+p':
            # Shield (static)
            dir.append([(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)])
        return dir
    # Inverses directions of moves depending on lower to UPPER as needed
    def mirror_directions(self):
        mirrored_directions = []
        for sublist in self.directions:
            mirrored_sublist = [(-dr, -dc) for (dr, dc) in sublist]
            mirrored_directions.append(mirrored_sublist)
        return mirrored_directions
    # Returns moves that can be made for pieces that can move continuously in a direction
    def valid_dynamic_helper(self, start_row, start_col, cur_piece, index, is_check):
        valid_moves = []
        for r, c in self.directions[index]:
            new_row, new_col = start_row + r, start_col + c
            while 0 <= new_row < self.BOARD_SIZE and 0 <= new_col < self.BOARD_SIZE:
                block_found = False
                for block in self.all_pieces:
                    # CASE: Piece can capture opposite team, not own
                    # CASE: Check, king can capture opposite team, not own
                    if not is_check:
                        if block[2].isupper() != cur_piece.isupper():
                            valid_moves.append((new_row, new_col))
                            break
                    elif is_check:
                        if (block[0], block[1]) == (new_row, new_col):
                            # CASE: Check, opponent piece can move one space past king
                            if block[2].lower() == 'd':
                                valid_moves.append((new_row+r, new_col+c))
                            valid_moves.append((new_row, new_col))
                            block_found = True
                            break  
                if block_found:
                    break
                valid_moves.append((new_row, new_col))
                new_row += r
                new_col += c
        return valid_moves
    # Returns moves that can be made for pieces that can only move once into a direction
    def valid_static_helper(self, start_row, start_col, cur_piece, index, is_check):
        valid_moves = []
        for r, c in self.directions[index]:
            new_row, new_col = start_row + r, start_col + c
            if 0 <= new_row < 5 and 0 <= new_col < 5:
                for block in self.all_pieces:
                    block_found = False
                    for block in self.all_pieces:
                        if block[0] == new_row and block[1] == new_col:
                            block_found = True
                            if not is_check:
                                if block[2].isupper() != cur_piece.isupper():
                                    valid_moves.append((new_row, new_col))
                                    break
                            elif is_check:
                                if (block[0], block[1]) == (new_row, new_col):
                                    valid_moves.append((new_row, new_col))
                                    block_found = True
                                    break
                    if block_found:
                        break
                    valid_moves.append((new_row, new_col))
        return valid_moves
    # Takes in pieces identity and start position to return valid moves
    def valid(self, cur_piece, start_position, is_check):
        lower_label = cur_piece.lower()
        start_row, start_col, = self.board_coordinates(start_position)
        self.directions = self.get_piece_moves(lower_label)
        if cur_piece.isupper():
            self.directions = self.mirror_directions()
        val_moves = []
        # Dynamic
        if lower_label in ['n', 'g']:
            val_moves.append(list(set(self.valid_dynamic_helper(start_row, start_col, cur_piece, 0, is_check))))
        # Static
        elif lower_label in ['d', 's', 'r', 'p', '+r', '+p']:
            val_moves.append(list(set(self.valid_static_helper(start_row, start_col, cur_piece, 0, is_check))))
        # Dyanimic then Static
        elif lower_label in ['+n', "+g"]:
            val_moves.append(list(set(self.valid_dynamic_helper(start_row, start_col, cur_piece, 0, is_check))))
            val_moves.append(list(set(self.valid_static_helper(start_row, start_col, cur_piece, 1, is_check))))
        val_moves = [move for sublist in val_moves for move in sublist]
        return val_moves
    # BASE: Base case of what gets updated upon a succesful drop turn
    def drop_move_base(self, row, col):
        self.check_piece_present()
        self._board[row][col] = self.piece_type.replace('+', '')
        self.last_move = [self.piece_type.isupper(), self.move]
        return
    # Removes trailing spaces for captured pieces array (for autograder)
    def capture_string(self, capture_arr):
        return ' '.join(capture_arr)
    # Retrieves (row, col, piece) for all pieces
    def get_pieces(self):
        pieces = []
        for row in range(len(self._board)):
            for col in range(len(self._board[0])):
                if self._board[row][col] != '__':
                    pieces.append((row, col, self._board[row][col]))
        return pieces
    # Based on moves played, determines who's turn it is and whose king is in check
    def determine_king(self):
        return 'D' if self.turn % 2 == 1 else 'd'
    # Heler function to retrieve king place like a1
    def king_info(self, king):
        for piece_info in self.all_pieces:
            if piece_info[2] == king:
                return piece_info
    # All of the information needed for the rest of a move turn
    def move_information(self, move_info):
        start, self.position = move_info[1], move_info[2]
        end_row, end_col = self.board_coordinates(self.position)
        tmp_board = copy.deepcopy(self._board)
        move_info_len = len(move_info)
        start_move = self.get_piece(start)
        self.piece_type = start_move
        tmp_start_piece = self.piece_type
        valid_moves = self.valid(self.piece_type, start, True)
        return start, end_row, end_col, tmp_board, move_info_len, tmp_start_piece, valid_moves
    def drop_information(self, move_info):
        piece_type, self.position = move_info[1], move_info[2]
        row, col = self.board_coordinates(move_info[2])
        cur_piece = self._board[row][col]
        tmp_board = copy.deepcopy(self._board)
        tmp_lower_cap = copy.deepcopy(self.lower_cap)
        tmp_upper_cap = copy.deepcopy(self.upper_cap)
        # This makes the piece uppercase or lowercase according to who's turn it is
        self.determine_turn(piece_type)
        return row, col, cur_piece, tmp_board, tmp_lower_cap, tmp_upper_cap
    # Helper to retrieve moves on the same team as opp_case, which is a leter from the same team
    # Opponent_moves stores (row, column, a1) and opponent_moves_dic stores {a1: [[0, 0]]}
    # Opponent_moves stores information of piece, opponent_moves_dic stores moves
    # No flat allows me to isolate moves made in a certain direction by a piece for manymoves
    def opponent_moves(self, opp_case, no_flat = None):
        opponent_pieces = []
        opponent_move_dic = {}
        for piece_info in self.all_pieces:
            if (piece_info[2]).isupper() == (opp_case).isupper():
                opponent_pieces.append(piece_info)
        opponent_moves = []
        for piece in opponent_pieces:
            piece_type = piece[2]
            if piece_type.isupper() == opp_case.isupper():
                piece_letter = self.coordinates_to_letter(piece[0], piece[1])
                piece_moves = self.valid(piece_type, piece_letter, True) if not no_flat else self.valid_block(piece_type, piece_letter, True)
                opponent_moves.append(piece_moves)
                opponent_move_dic[piece_letter] = piece_moves
        return opponent_moves, opponent_move_dic
    # Returns the number of moves that the opponent_moves has the king in check
    def count_check(self, opponent_moves):
        check = 0
        for opponent_piece in opponent_moves:
            for move in opponent_piece:
                if self.king_coord == move:
                    check += 1
        return check
    # Returns the moves a king could make that would result in a loss
    def check_move(self, king_moves, opponent_moves_flat):
        check_move = []
        for king_move in king_moves:
            for move in opponent_moves_flat:
                if king_move == (move[0], move[1]):
                    check_move.append(king_move)
        return check_move
    # King information that may be of use when verifying a check
    def king_information(self):
        self.king = self.determine_king()
        king_info = self.king_info(self.king)
        self.king_coord = (king_info[0], king_info[1])
        self.king_letter = self.coordinates_to_letter(king_info[0], king_info[1])
        king_moves = self.valid(king_info[2], self.king_letter, False)
        return king_info, king_moves
    # Returns the pieces and its move from the opponent player that have the players' king in check
    def opp_info(self, opponent_move_dic):
        opp_info = {}
        for key, value in opponent_move_dic.items():
            if self.king_coord in value:
                for move in self.all_pieces:
                    if self.coordinates_to_letter(move[0], move[1]) == key:
                        opp_info[key] = value
                        opp_info[key].append((move[0], move[1]))
        return opp_info
    # Returns the opponent moves that are in the direction from a piece to the king
    # For example, if a piece moves horizontally it identifies which horizontal direction
    def opponent_moves_to_king(self, opponent_move_dic_no_flat, king_info):
        # First identifying the moves
        opponent_moves_to_king = []
        for _, opp_value in opponent_move_dic_no_flat.items():
            for opp_arr in opp_value:
                for opp_moves in opp_arr:
                    king_row, king_col = king_info[0], king_info[1]
                    for move_row, move_col in opp_moves:
                        if (move_row, move_col) == (king_row, king_col):
                            opponent_moves_to_king.append(opp_moves)
                            break
                    else:
                        continue
                    break
        # Filtering the moves that are out of bounds
        update_to_king = []
        for direction in opponent_moves_to_king:
            for move in direction:
                if move[0] >= 0 and move[1] < self.BOARD_SIZE-1 and move != (king_info[0], king_info[1]):
                    update_to_king.append(move)
        return update_to_king
    # Returns moves a player can play to drop a piece to not lose
    def check_drop_moves(self, update_to_king):
        hand = self.upper_cap if self.king.isupper() else self.lower_cap
        drop_moves = []
        for piece in hand:
            for move in update_to_king:
                if self.piece_type:
                    # CHECK valid drop
                    if (self.piece_type.lower() == 'p' and self.preview_drop()) or (self.piece_type.lower() == 'p' and self.preview_double()):
                        continue
                    tmp_letter = self.coordinates_to_letter(move[0], move[1])
                    drop_moves.append((piece.lower(), tmp_letter))
        return drop_moves
    # Updates moves to king to include opponent piece puttin king in check
    # Updated in consideration that youo can't drop a piece onto another piece
    def update_to_king(self, opp_info, update_to_king):
        for key, _ in opp_info.items():
            key_r, key_c = self.board_coordinates(key)
            update_to_king.append((key_r, key_c))
        return update_to_king
    # Returns moves of pieces other than the king to block the check
    def alternative_moves(self, player_move_dic, update_to_king):
        alternative_moves = []
        for key, value in player_move_dic.items():
            for move in update_to_king:
                if key == self.king_letter:
                    continue
                for potential_move in value:
                    if move == potential_move:
                        end_letter = self.coordinates_to_letter(move[0], move[1])
                        alternative_moves.append((key, end_letter))
        return alternative_moves
    # Returns moves that can be made by the king to move out of check
    def king_moves(self, king_moves, check_move):
        king_remaining_moves = list(set(king_moves)-set(check_move))
        king_letter_moves = []
        for move in king_remaining_moves:
            letter = self.coordinates_to_letter(move[0], move[1])
            king_letter_moves.append((self.king_letter, letter))
        return king_remaining_moves, king_letter_moves
    # Output for checkmate
    def checkmate_end(self, king_moves, check_move,  edge):
        if len(king_moves) - len(check_move) == 0:
            winner = self.upper_winner(self.king, False)
            if edge:
                winner = self.upper_winner(self.king, True)
            print(winner, 'player wins.  Checkmate.')
            sys.exit()
    # Output for check
    def check_end(self, king_moves, check_move, check, edge):
        king_remaining_moves = list(set(king_moves)-set(check_move))
        if check != 0:
            winner = self.upper_winner(self.king, False)
            if edge:
                winner = self.upper_winner(self.king, True)
            else:
                print(winner, "player is in check!")
                print("Available moves:")
                king_remaining_moves = sorted(king_remaining_moves)
                for move in king_remaining_moves:
                    move_letter = self.coordinates_to_letter(move[0], move[1])
                    print("move", self.king_letter, move_letter)
    # Checks if a player is in check
    def check(self, edge=None):
        self.all_pieces = self.get_pieces()
        king_info, king_moves = self.king_information()
        opp_case = self.king.lower() if self.king.isupper() else self.king.upper()
        opponent_moves, opponent_move_dic = self.opponent_moves(opp_case)
        check = self.count_check(opponent_moves)
        opponent_moves_flat = list(set([move for sublist in opponent_moves for move in sublist]))
        check_move = self.check_move(king_moves, opponent_moves_flat)
        # END: Checkmate
        self.checkmate_end(king_moves, check_move, edge)
        opp_info = self.opp_info(opponent_move_dic)
        _, player_move_dic = self.opponent_moves(self.king)
        _, opponent_move_dic_no_flat = self.opponent_moves(opp_case, True)
        # CASE: Many moves is only an option if only one piece is keeping the king in check
        if len(opp_info) == 1:
            # Determine continuous direction that opponent piece makes to king
            update_to_king = self.opponent_moves_to_king(opponent_move_dic_no_flat, king_info)
            # CASE: Determine moves where a piece in player hand can be dropped to block check
            drop_moves = self.check_drop_moves(update_to_king)
            # Update moves to include the position of the piece putting king in check
            update_to_king = self.update_to_king(opp_info, update_to_king)
            # CASE: Determine player moves that aren't king to block
            alternative_moves = self.alternative_moves(player_move_dic, update_to_king)
        else:
            drop_moves, alternative_moves = [], []
        # CASE: Determine moves that can be made by the king to move out of check
        king_moves, king_letter_moves = self.king_moves(king_moves, check_move)
        # Final output if the player is in check and there are many moves to make
        self.many_moves_end(check, king_info, drop_moves, king_letter_moves, alternative_moves)
        # END: Check
        self.check_end(king_moves, check_move, check, edge)
        # ADDED, because I added a temporary + 1 for some case
    # Add capture to capture hand of appropriate player
    def drop_remove_cap(self, potential_capture):
        if potential_capture != 1:
            if potential_capture.islower():
                self.upper_cap.append(potential_capture.upper().strip()) 
            else:
                self.lower_cap.append(potential_capture.lower().strip())
        return
    # When piece is dropped, removes piece from capture hand
    def check_piece_present(self):
        if self.piece_type in self.upper_cap:
            self.upper_cap.remove(self.piece_type)
        elif self.piece_type in self.lower_cap:
            self.lower_cap.remove(self.piece_type)
        return
    # CASE: Preview dropped in state to check the other king
    # CASE: Piece dropped immediately causing mate
    def drop_preview_check(self):
        cur_moves = self.valid(self.piece_type, self.position, True)
        opp_case = self.piece_type.lower() if self.piece_type.isupper() else self.piece_type.upper()
        for piece in self.all_pieces:
            if piece[2].islower() == opp_case.islower() and piece[2].lower() == 'd':
                k_row, k_col = piece[0], piece[1]
        for move in cur_moves:
            if (k_row, k_col) == move:
                return True
        return False
    # CASE: Move puts move player in check illegally
    def move_check(self):
        self.all_pieces = self.get_pieces()
        king = self.determine_king()
        king_info = self.king_info(king)
        opp_case = king.lower() if king.isupper() else king.upper()
        opponent_moves, _ = self.opponent_moves(opp_case)
        for opponent_piece in opponent_moves:
            for move in opponent_piece:
                if (king_info[0], king_info[1]) == move:
                    return True
        return False
    # CASE: Immediate preview drop mate
    def preview_drop(self):
        return self.promotion_zone(self.piece_type, self.position)
    # CASE: Preview illegal move to promotion zone
    def preview_no_promotion_area(self):
        _, col = self.board_coordinates(self.position)
        if self.piece_type.islower():
            return col == 0
        return col == self.BOARD_SIZE - 1
    # CASE: Forced preview promotion
    def preview_auto_promote(self):
        _, col = self.board_coordinates(self.position)
        if (self.piece_type == 'P' and col == 0) or (self.piece_type == 'p' and col == self.BOARD_SIZE-1):
            self.piece_type = '+' + self.piece_type
        return
    # CASE: Double preview drop
    def preview_double(self):
        row, _ = self.board_coordinates(self.position)
        all_pieces = self.get_pieces()
        compare = []
        for piece in all_pieces:
            if piece[2] == self.piece_type:
                compare.append(piece)
        for piece in compare:
            if row == piece[0]:
                return True
        return False
    def drop_own(self, cur_piece):
        for _, _, piece_type in self.all_pieces:
            if cur_piece.isupper() == piece_type.isupper():
                return True
        return False
    # END: Generic output for illegal moves made
    def end_early(self):
        winner = self.upper_winner(self.piece_type, True)
        self.illegal_tuple = (True, winner) 
        self.last_move = [self.piece_type.isupper(), self.move]
        return
    # END: Print the moves if ther are many moves to block a check
    def many_moves_end(self, check, king_info, drop_moves, king_letter_moves, alternative_moves):
        if check != 0:
            # Person who didn't make last move in check is in check
            winner = self.upper_winner(self.piece_type, True) if king_info[2].isupper() else self.upper_winner(self.piece_type, False)
            print(winner, "player is in check!")
            print("Available moves:")
            if len(drop_moves) != 0:
                moves = sorted(drop_moves)
                for move in moves:
                    print('drop',move[0], move[1])
            moves = sorted(king_letter_moves + alternative_moves)
            for move in moves:
                print("move", move[0], move[1])
            print('UPPER>') if king_info[2].isupper() else print('lower>')
            sys.exit()
    # Helper to output
    def report_recent_move(self):
        print('UPPER player action:', self.last_move[1]) if self.last_move[0] else print('lower player action:', self.last_move[1])
    # Helper to output
    def report_end_capture(self):
        upper = "Captures UPPER: " + self.capture_string(self.upper_cap)
        lower = "Captures lower: " + self.capture_string(self.lower_cap)
        print(upper.strip())
        print(lower.strip())
    # Helper to output
    def illegal(self):
        if self.illegal_tuple[0]:
            print(self.illegal_tuple[1], 'player wins.  Illegal move.')
    # END: Too many moves
    def tie_game(self):
        if self.turn == 400:
            self.check(True)
        if self.turn > 399:
            print()
            print('Tie game.  Too many moves.')
            sys.exit()
    # Helper to output
    def report_next_player_output(self):
        if self.interactive:
            if not self.illegal_tuple[0]:
                return input('lower>') if self.last_move[0] else input('UPPER>')
        if not self.illegal_tuple[0]:
            print('lower>') if self.last_move[0] else print('UPPER>')
            return
    # END: Output if a valid move in interactive or all moves in file are made
    def final_print_f(self):
        self.report_recent_move()
        print(self.__str__())
        self.report_end_capture()
        self.tie_game()
        print()
        self.check()
        self.illegal()
        if self.interactive:
            return self.report_next_player_output()
        else:
            self.report_next_player_output()
    # END: Output for an illegal output, there is no next move
    # END: Output for dropping a piece that immediately causes a mate
    # END: Output of attempt to make an illegal promotion
    # End state for moving own piece to be in check illegaly dropping own piece
    # End state for dropping 
    def illegal_output(self):
        self.end_early()
        self.report_recent_move()
        print(self.__str__())
        self.report_end_capture()
        print()
        self.illegal()
        sys.exit()
    # Helper for pieces with continuous direction moves, but directions are not flattened
    def valid_dynamic_block(self, start_row, start_col, cur_piece, index, is_check):
        valid_moves = []
        for direction in self.directions[index]:
            temp_valid_moves = []
            r, c = direction
            new_row, new_col = start_row + r, start_col + c
            while 0 <= new_row < self.BOARD_SIZE and 0 <= new_col < self.BOARD_SIZE:
                block_found = False
                for block in self.all_pieces:
                    if not is_check:
                        if block[2].isupper() != cur_piece.isupper():
                            temp_valid_moves.append((new_row, new_col))
                            break
                    elif is_check:
                        if (block[0], block[1]) == (new_row, new_col):
                            if block[2].lower() == 'd' and block[2].isupper() != cur_piece.isupper():
                                temp_valid_moves.append((new_row, new_col))
                            block_found = True
                            break  
                if block_found:
                    break
                temp_valid_moves.append((new_row, new_col))
                new_row += r
                new_col += c
            valid_moves.append(temp_valid_moves)
        return valid_moves
    # Helper for pieces without continuous direction moves, but directions are not flattened
    def valid_static_block(self, start_row, start_col, cur_piece, index, is_check):
        valid_moves = []
        for direction in self.directions[index]:
            temp_valid_moves = []
            r, c = direction
            new_row, new_col = start_row + r, start_col + c
            if 0 <= new_row < 5 and 0 <= new_col < 5:
                for block in self.all_pieces:
                    block_found = False
                    for block in self.all_pieces:
                        if block[0] == new_row and block[1] == new_col:
                            block_found = True
                            if not is_check:
                                if block[2].isupper() != cur_piece.isupper():
                                    temp_valid_moves.append((new_row, new_col))
                                    break
                            elif is_check:
                                if (block[0], block[1]) == (new_row, new_col):
                                    temp_valid_moves.append((new_row, new_col))
                                    block_found = True
                                    break
                    if block_found:
                        break
                    temp_valid_moves.append((new_row, new_col))
            valid_moves.append(temp_valid_moves)
        return valid_moves
    # Returns valid moves for a piece in an unflattened array
    def valid_block(self, cur_piece, start_position, is_check):
        lower_label = cur_piece.lower()
        start_row, start_col = self.board_coordinates(start_position)
        self.directions = self.get_piece_moves(lower_label)
        if cur_piece.isupper():
            self.directions = self.mirror_directions()
        val_moves = []
        # Dynamic
        if lower_label in ['n', 'g']:
            val_moves.append(self.valid_dynamic_block(start_row, start_col, cur_piece, 0, is_check))
        # Static
        elif lower_label in ['d', 's', 'r', 'p', '+r', '+p']:
            val_moves.append(self.valid_static_block(start_row, start_col, cur_piece, 0, is_check))
        # Dynamic then Static
        elif lower_label in ['+n', "+g"]:
            val_moves.append(self.valid_dynamic_block(start_row, start_col, cur_piece, 0, is_check))
            val_moves.append(self.valid_static_block(start_row, start_col, cur_piece, 1, is_check))
        return val_moves
    def shogi_main(self, move):
        self.all_pieces = self.get_pieces()
        for _ in range(1):
            move_info = move.strip().split()
            self.move = move
            if move_info[0] == "move":
                start, end_row, end_col, tmp_board, move_info_len, tmp_start_piece, valid_moves = self.move_information(move_info)
                if(end_row, end_col) in valid_moves:
                    # CASE: Forced preview promotion
                    if self.piece_type.lower() == 'p':
                        self.preview_auto_promote()
                    # CASE: Normal promotion
                    elif move_info_len == 4:
                        self.piece_type = self.piece_promote(self.piece_type, start)
                    # CASE: Illegal promoted promotion
                    # CASE: Preview illegal move to promotion zone
                    if not self.piece_type or ((self.piece_type.lower() == '+p') and self.preview_no_promotion_area()):
                        self.piece_type = tmp_start_piece
                        self.illegal_output()
                    # BASE
                    self.remove_piece(start)
                    potential_capture = self.add_piece()
                    # CASE: Move puts move player in check illegally
                    if self.move_check() and self.piece_type.lower() == 'd':
                        self._board = tmp_board
                        self.piece_type = tmp_start_piece
                        self.illegal_output()
                    self.drop_remove_cap(potential_capture)
                else:
                    self.end_early()
                    break
            elif move_info[0] == "drop":
                row, col, cur_piece, tmp_board, tmp_lower_cap, tmp_upper_cap = self.drop_information(move_info)
                if cur_piece == '__':
                    # Sets the piece type to upper or lower
                    # CASE: Drop piece not in hand
                    # CASE: Drop empty hand
                    # CASE: Drop opponent's piece
                    # CASE: Immediate preview drop mate
                    # CASE: Double preview drop
                    if ((self.piece_type.islower() and self.piece_type not in self.lower_cap) or (self.piece_type.isupper() and self.piece_type not in self.upper_cap)) or len(self.upper_cap) == 0 or len(self.lower_cap) == 0 or (self.piece_type not in self.upper_cap and self.piece_type not in self.lower_cap) or (self.piece_type.lower() == 'p' and self.preview_drop()) or (self.piece_type.lower() == 'p' and self.preview_double()):
                        self.illegal_output()
                    # BASE
                    self.drop_move_base(row, col)
                else:
                    if cur_piece == self.piece_type:
                        self.end_early()
                    # CASE: Illegal drop on own piece
                    # CASE: Piece dropped immediately causing mate
                    if self.drop_own(cur_piece) or (self.drop_preview_check() and self.piece_type.lower() == 'p'):
                        self.illegal_output()
                # CASE: Preview dropped in state to check the other king
                if self.drop_preview_check() and self.piece_type.lower() == 'p':
                    self._board = tmp_board
                    self.upper_cap = tmp_upper_cap
                    self.lower_cap = tmp_lower_cap
                    self.illegal_output()
            self.last_move = [self.piece_type.isupper(), move]
            self.turn += 1
        return
    # Function call to run test file mode
    def play_file(self):
        self.init_board()
        for move in self.move_state:
            self.shogi_main(move)
        self.final_print_f()
    # Function call to play interactive mode
    def play_interactive(self):
        tmp = None
        move = self.start_output_interactive()
        while move != tmp:
            tmp = move
            self.shogi_main(move)
            move = self.final_print_f()