import sys
from utils import parseTestCase
import board
import copy

def main():
    """
    Main function to read terminal input
    """
    if sys.argv[1] == '-f':

        dic = parseTestCase(sys.argv[2])
        initialState, upperCap, lowerCap, moveState = dic['initialPieces'], dic['upperCaptures'], dic['lowerCaptures'], dic['moves']
        turn, illegal_tuple = 0, (False, '')
        move, last_move, piece_type, position = None, None, None, None
        game_board = board.Board(move, moveState, initialState, upperCap, lowerCap, illegal_tuple, turn, last_move, piece_type, position)
        game_board.play_file()

    # Interactive mode
    if sys.argv[1] == '-i':
        
        upperCap, lowerCap = [], []
        turn, illegal_tuple = 0, (False, '')
        move, last_move, moveState, initialState, piece_type, position = None, None, None, None, None, None
        game_board = board.Board(move, moveState, initialState, upperCap, lowerCap, illegal_tuple, turn, last_move, piece_type, position, True)
        game_board.play_interactive()
        

if __name__ == "__main__":
    main()