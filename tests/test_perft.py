
import chess
from engine.move_generator import BoardState, generate_legal_moves

# Known Perft node counts for the standard starting position
START_POS_PERFT = {
    1: 20,
    2: 400,
    3: 8902,
    4: 197281,
    # 5: 4865609,  # Keep up to 4 for reasonable test time
}

KIWIPETE_FEN = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"
KIWIPETE_PERFT = {
    1: 48,
    2: 2039,
    3: 97862,
    # 4: 4085603,
}

POSITION_3_FEN = "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1"
POSITION_3_PERFT = {
    1: 14,
    2: 191,
    3: 2812,
    4: 43238,
}

POSITION_4_FEN = "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1"
POSITION_4_PERFT = {
    1: 6,
    2: 264,
    3: 9467,
}

def custom_perft(board: chess.Board, depth: int) -> int:
    if depth == 0:
        return 1

    nodes = 0
    # Instantiate BoardState to test the custom move generator
    state = BoardState(board.fen())
    custom_moves = generate_legal_moves(state)
    
    for custom_move in custom_moves:
        # Use python-chess to handle state transitions
        move = chess.Move.from_uci(custom_move.uci())
        board.push(move)
        nodes += custom_perft(board, depth - 1)
        board.pop()
        
    return nodes

def test_perft_startpos():
    """Test Perft node counts for the starting position using custom move_generator."""
    board = chess.Board()
    for depth, expected_nodes in START_POS_PERFT.items():
        board.reset()
        nodes = custom_perft(board, depth)
        assert nodes == expected_nodes, f"StartPos Perft depth {depth} failed: expected {expected_nodes}, got {nodes}"

def test_perft_kiwipete():
    """Test Perft node counts for the Kiwipete position (Position 2)."""
    board = chess.Board(KIWIPETE_FEN)
    for depth, expected_nodes in KIWIPETE_PERFT.items():
        board.set_fen(KIWIPETE_FEN)
        nodes = custom_perft(board, depth)
        assert nodes == expected_nodes, f"Kiwipete Perft depth {depth} failed: expected {expected_nodes}, got {nodes}"

def test_perft_position_3():
    """Test Perft node counts for Position 3."""
    board = chess.Board(POSITION_3_FEN)
    for depth, expected_nodes in POSITION_3_PERFT.items():
        board.set_fen(POSITION_3_FEN)
        nodes = custom_perft(board, depth)
        assert nodes == expected_nodes, f"Position 3 Perft depth {depth} failed: expected {expected_nodes}, got {nodes}"

def test_perft_position_4():
    """Test Perft node counts for Position 4."""
    board = chess.Board(POSITION_4_FEN)
    for depth, expected_nodes in POSITION_4_PERFT.items():
        board.set_fen(POSITION_4_FEN)
        nodes = custom_perft(board, depth)
        assert nodes == expected_nodes, f"Position 4 Perft depth {depth} failed: expected {expected_nodes}, got {nodes}"

