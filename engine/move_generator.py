import typing
from typing import List, Optional, Tuple, Dict

class Move:
    def __init__(self, from_square: int, to_square: int, promotion: Optional[str] = None):
        self.from_square = from_square
        self.to_square = to_square
        self.promotion = promotion

    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return (self.from_square == other.from_square and 
                self.to_square == other.to_square and 
                self.promotion == other.promotion)
        
    def uci(self) -> str:
        f = "abcdefgh"
        r = "12345678"
        promo = self.promotion.lower() if self.promotion else ""
        return f[self.from_square % 8] + r[self.from_square // 8] + \
               f[self.to_square % 8] + r[self.to_square // 8] + promo

    def __repr__(self):
        return self.uci()


KNIGHT_MOVES = [0] * 64
KING_MOVES = [0] * 64

def init_tables():
    for sq in range(64):
        r = sq // 8
        f = sq % 8
        
        # Knight
        k_attacks = 0
        for dr, df in [(2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)]:
            nr, nf = r + dr, f + df
            if 0 <= nr < 8 and 0 <= nf < 8:
                k_attacks |= (1 << (nr * 8 + nf))
        KNIGHT_MOVES[sq] = k_attacks
        
        # King
        kg_attacks = 0
        for dr in [-1, 0, 1]:
            for df in [-1, 0, 1]:
                if dr == 0 and df == 0: continue
                nr, nf = r + dr, f + df
                if 0 <= nr < 8 and 0 <= nf < 8:
                    kg_attacks |= (1 << (nr * 8 + nf))
        KING_MOVES[sq] = kg_attacks

init_tables()

RAY_ATTACKS = {
    8: [0] * 64, 1: [0] * 64, -8: [0] * 64, -1: [0] * 64,
    9: [0] * 64, 7: [0] * 64, -7: [0] * 64, -9: [0] * 64
}

def init_rays():
    for sq in range(64):
        r = sq // 8
        f = sq % 8
        for dr, df in [(1,0), (0,1), (-1,0), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]:
            if (dr, df) == (1,0): d = 8
            elif (dr, df) == (0,1): d = 1
            elif (dr, df) == (-1,0): d = -8
            elif (dr, df) == (0,-1): d = -1
            elif (dr, df) == (1,1): d = 9
            elif (dr, df) == (1,-1): d = 7
            elif (dr, df) == (-1,1): d = -7
            elif (dr, df) == (-1,-1): d = -9
            
            ray = 0
            cr, cf = r + dr, f + df
            while 0 <= cr < 8 and 0 <= cf < 8:
                ray |= (1 << (cr * 8 + cf))
                cr += dr
                cf += df
            RAY_ATTACKS[d][sq] = ray

init_rays()

def get_positive_ray_attacks(sq: int, occupied: int, d: int) -> int:
    attacks = RAY_ATTACKS[d][sq]
    blockers = attacks & occupied
    if blockers:
        first_blocker = (blockers & -blockers).bit_length() - 1
        attacks ^= RAY_ATTACKS[d][first_blocker]
    return attacks

def get_negative_ray_attacks(sq: int, occupied: int, d: int) -> int:
    attacks = RAY_ATTACKS[d][sq]
    blockers = attacks & occupied
    if blockers:
        first_blocker = blockers.bit_length() - 1
        attacks ^= RAY_ATTACKS[d][first_blocker]
    return attacks

def get_bishop_attacks(sq: int, occupied: int) -> int:
    return (get_positive_ray_attacks(sq, occupied, 9) |
            get_positive_ray_attacks(sq, occupied, 7) |
            get_negative_ray_attacks(sq, occupied, -7) |
            get_negative_ray_attacks(sq, occupied, -9))

def get_rook_attacks(sq: int, occupied: int) -> int:
    return (get_positive_ray_attacks(sq, occupied, 8) |
            get_positive_ray_attacks(sq, occupied, 1) |
            get_negative_ray_attacks(sq, occupied, -8) |
            get_negative_ray_attacks(sq, occupied, -1))

def get_queen_attacks(sq: int, occupied: int) -> int:
    return get_bishop_attacks(sq, occupied) | get_rook_attacks(sq, occupied)


class BoardState:
    """A generic board state object to represent the board using bitboards."""
    def __init__(self, fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        self.pieces: Dict[str, int] = {}
        self.turn = 'w'
        self.castling = ""
        self.ep_square: Optional[int] = None
        self.halfmove = 0
        self.fullmove = 1
        if fen:
            self.load_fen(fen)
            
    def load_fen(self, fen: str):
        parts = fen.split()
        board_part = parts[0]
        
        self.pieces = {p: 0 for p in "PNBRQKpnbrqk"}
        
        rank = 7
        file = 0
        for char in board_part:
            if char == '/':
                rank -= 1
                file = 0
            elif char.isdigit():
                file += int(char)
            else:
                sq = rank * 8 + file
                self.pieces[char] |= (1 << sq)
                file += 1
                
        self.turn = parts[1] if len(parts) > 1 else 'w'
        self.castling = parts[2] if len(parts) > 2 else '-'
        
        ep_str = parts[3] if len(parts) > 3 else '-'
        if ep_str != '-' and len(ep_str) == 2 and ep_str[0] in "abcdefgh" and ep_str[1] in "12345678":
            f = "abcdefgh".index(ep_str[0])
            r = int(ep_str[1]) - 1
            self.ep_square = r * 8 + f
        else:
            self.ep_square = None


class BoardStateAdapter:
    """Adapts any provided board_state into a bitboard representation for the generator."""
    def __init__(self, state):
        self.pieces = getattr(state, 'pieces', {}).copy()
        
        turn_attr = getattr(state, 'turn', 'w')
        if isinstance(turn_attr, bool):
            self.turn = 'w' if turn_attr else 'b'
        else:
            self.turn = turn_attr
            
        self.ep_square = getattr(state, 'ep_square', None)
        self.castling = getattr(state, 'castling', getattr(state, 'castling_rights', 'KQkq'))
        
        self.update_occupancies()

    def update_occupancies(self):
        self.white_occ = 0
        for p in ['P', 'N', 'B', 'R', 'Q', 'K']:
            self.white_occ |= self.pieces.get(p, 0)
            
        self.black_occ = 0
        for p in ['p', 'n', 'b', 'r', 'q', 'k']:
            self.black_occ |= self.pieces.get(p, 0)
            
        self.all_occ = self.white_occ | self.black_occ

    def clone(self):
        new_state = BoardStateAdapter.__new__(BoardStateAdapter)
        new_state.pieces = self.pieces.copy()
        new_state.turn = self.turn
        new_state.ep_square = self.ep_square
        new_state.castling = self.castling
        new_state.white_occ = self.white_occ
        new_state.black_occ = self.black_occ
        new_state.all_occ = self.all_occ
        return new_state

    def apply_move(self, move: Move):
        is_white = self.turn == 'w'
        
        # 1. Find and remove piece from from_square
        moving_piece = None
        for p, bb in self.pieces.items():
            if bb & (1 << move.from_square):
                moving_piece = p
                self.pieces[p] &= ~(1 << move.from_square)
                break
        
        if not moving_piece:
            return

        # 2. Remove captured piece from to_square (if any)
        for p, bb in self.pieces.items():
            if bb & (1 << move.to_square):
                self.pieces[p] &= ~(1 << move.to_square)
                break
                
        # Handle En Passant capture
        if moving_piece.lower() == 'p' and move.to_square == self.ep_square:
            cap_sq = move.to_square - 8 if is_white else move.to_square + 8
            if 0 <= cap_sq < 64:
                cap_piece = 'p' if is_white else 'P'
                if cap_piece in self.pieces:
                    self.pieces[cap_piece] &= ~(1 << cap_sq)

        # Handle Castling rook move
        if moving_piece.lower() == 'k' and abs(move.from_square - move.to_square) == 2:
            if move.to_square == 6: # wk
                self.pieces['R'] = (self.pieces.get('R', 0) & ~(1 << 7)) | (1 << 5)
            elif move.to_square == 2: # wq
                self.pieces['R'] = (self.pieces.get('R', 0) & ~(1 << 0)) | (1 << 3)
            elif move.to_square == 62: # bk
                self.pieces['r'] = (self.pieces.get('r', 0) & ~(1 << 63)) | (1 << 61)
            elif move.to_square == 58: # bq
                self.pieces['r'] = (self.pieces.get('r', 0) & ~(1 << 56)) | (1 << 59)

        # 3. Add piece to to_square
        if move.promotion:
            promo = move.promotion.upper() if is_white else move.promotion.lower()
            self.pieces[promo] = self.pieces.get(promo, 0) | (1 << move.to_square)
        else:
            self.pieces[moving_piece] |= (1 << move.to_square)

        self.update_occupancies()


def is_attacked(sq: int, by_white: bool, state: BoardStateAdapter) -> bool:
    occ = state.all_occ
    if by_white:
        if get_bishop_attacks(sq, occ) & (state.pieces.get('B', 0) | state.pieces.get('Q', 0)): return True
        if get_rook_attacks(sq, occ) & (state.pieces.get('R', 0) | state.pieces.get('Q', 0)): return True
        if KNIGHT_MOVES[sq] & state.pieces.get('N', 0): return True
        if KING_MOVES[sq] & state.pieces.get('K', 0): return True
        
        r = sq // 8
        f = sq % 8
        if r > 0:
            if f > 0 and (state.pieces.get('P', 0) & (1 << (sq - 9))): return True
            if f < 7 and (state.pieces.get('P', 0) & (1 << (sq - 7))): return True
    else:
        if get_bishop_attacks(sq, occ) & (state.pieces.get('b', 0) | state.pieces.get('q', 0)): return True
        if get_rook_attacks(sq, occ) & (state.pieces.get('r', 0) | state.pieces.get('q', 0)): return True
        if KNIGHT_MOVES[sq] & state.pieces.get('n', 0): return True
        if KING_MOVES[sq] & state.pieces.get('k', 0): return True
        
        r = sq // 8
        f = sq % 8
        if r < 7:
            if f > 0 and (state.pieces.get('p', 0) & (1 << (sq + 7))): return True
            if f < 7 and (state.pieces.get('p', 0) & (1 << (sq + 9))): return True
    return False


def generate_pseudo_legal_moves(state: BoardStateAdapter) -> List[Move]:
    moves = []
    is_white = state.turn == 'w'
    
    us_occ = state.white_occ if is_white else state.black_occ
    enemy_occ = state.black_occ if is_white else state.white_occ
    all_occ = state.all_occ
    
    # Pawns
    pawn_char = 'P' if is_white else 'p'
    pawns = state.pieces.get(pawn_char, 0)
    
    while pawns:
        sq = (pawns & -pawns).bit_length() - 1
        pawns &= pawns - 1
        
        r = sq // 8
        f = sq % 8
        
        dir_fwd = 8 if is_white else -8
        start_rank = 1 if is_white else 6
        promo_rank = 7 if is_white else 0
        
        # Single push
        fwd_sq = sq + dir_fwd
        if not (all_occ & (1 << fwd_sq)):
            if (fwd_sq // 8) == promo_rank:
                for p in ['Q', 'R', 'B', 'N']:
                    moves.append(Move(sq, fwd_sq, promotion=p))
            else:
                moves.append(Move(sq, fwd_sq))
                # Double push
                if r == start_rank:
                    dbl_sq = fwd_sq + dir_fwd
                    if not (all_occ & (1 << dbl_sq)):
                        moves.append(Move(sq, dbl_sq))
        
        # Captures
        cap_dirs = [(1, -1), (1, 1)] if is_white else [(-1, -1), (-1, 1)]
        for dr, df in cap_dirs:
            nr, nf = r + dr, f + df
            if 0 <= nr < 8 and 0 <= nf < 8:
                cap_sq = nr * 8 + nf
                if enemy_occ & (1 << cap_sq):
                    if nr == promo_rank:
                        for p in ['Q', 'R', 'B', 'N']:
                            moves.append(Move(sq, cap_sq, promotion=p))
                    else:
                        moves.append(Move(sq, cap_sq))
                elif state.ep_square == cap_sq:
                    moves.append(Move(sq, cap_sq))
                    
    # Knights
    knight_char = 'N' if is_white else 'n'
    knights = state.pieces.get(knight_char, 0)
    while knights:
        sq = (knights & -knights).bit_length() - 1
        knights &= knights - 1
        attacks = KNIGHT_MOVES[sq] & ~us_occ
        while attacks:
            to_sq = (attacks & -attacks).bit_length() - 1
            attacks &= attacks - 1
            moves.append(Move(sq, to_sq))
            
    # Bishops
    bishop_char = 'B' if is_white else 'b'
    bishops = state.pieces.get(bishop_char, 0)
    while bishops:
        sq = (bishops & -bishops).bit_length() - 1
        bishops &= bishops - 1
        attacks = get_bishop_attacks(sq, all_occ) & ~us_occ
        while attacks:
            to_sq = (attacks & -attacks).bit_length() - 1
            attacks &= attacks - 1
            moves.append(Move(sq, to_sq))
            
    # Rooks
    rook_char = 'R' if is_white else 'r'
    rooks = state.pieces.get(rook_char, 0)
    while rooks:
        sq = (rooks & -rooks).bit_length() - 1
        rooks &= rooks - 1
        attacks = get_rook_attacks(sq, all_occ) & ~us_occ
        while attacks:
            to_sq = (attacks & -attacks).bit_length() - 1
            attacks &= attacks - 1
            moves.append(Move(sq, to_sq))
            
    # Queens
    queen_char = 'Q' if is_white else 'q'
    queens = state.pieces.get(queen_char, 0)
    while queens:
        sq = (queens & -queens).bit_length() - 1
        queens &= queens - 1
        attacks = get_queen_attacks(sq, all_occ) & ~us_occ
        while attacks:
            to_sq = (attacks & -attacks).bit_length() - 1
            attacks &= attacks - 1
            moves.append(Move(sq, to_sq))
            
    # King
    king_char = 'K' if is_white else 'k'
    kings = state.pieces.get(king_char, 0)
    if kings:
        sq = (kings & -kings).bit_length() - 1
        attacks = KING_MOVES[sq] & ~us_occ
        while attacks:
            to_sq = (attacks & -attacks).bit_length() - 1
            attacks &= attacks - 1
            moves.append(Move(sq, to_sq))
            
        # Castling
        if is_white:
            if 'K' in state.castling:
                if not (all_occ & ((1 << 5) | (1 << 6))):
                    moves.append(Move(4, 6))
            if 'Q' in state.castling:
                if not (all_occ & ((1 << 1) | (1 << 2) | (1 << 3))):
                    moves.append(Move(4, 2))
        else:
            if 'k' in state.castling:
                if not (all_occ & ((1 << 61) | (1 << 62))):
                    moves.append(Move(60, 62))
            if 'q' in state.castling:
                if not (all_occ & ((1 << 57) | (1 << 58) | (1 << 59))):
                    moves.append(Move(60, 58))

    return moves


def is_castling_move(move: Move, state: BoardStateAdapter) -> bool:
    king_char = 'K' if state.turn == 'w' else 'k'
    if (state.pieces.get(king_char, 0) & (1 << move.from_square)) != 0:
        if abs(move.from_square - move.to_square) == 2:
            return True
    return False

def is_castling_legal(move: Move, state: BoardStateAdapter, is_white: bool) -> bool:
    king_sq = move.from_square
    if is_attacked(king_sq, not is_white, state):
        return False
    step = 1 if move.to_square > move.from_square else -1
    mid_sq = king_sq + step
    if is_attacked(mid_sq, not is_white, state):
        return False
    return True


def generate_legal_moves(board_state) -> List[Move]:
    """
    Generates a list of completely legal chess moves given a board_state.
    board_state can be any object with pieces (dict of bitboards), turn, castling, and ep_square,
    or an instance of BoardState.
    """
    state = BoardStateAdapter(board_state)
    pseudo_moves = generate_pseudo_legal_moves(state)
    legal_moves = []
    
    is_white = state.turn == 'w'
    king_char = 'K' if is_white else 'k'
    
    for move in pseudo_moves:
        # Check castling legality first (can't castle out of or through check)
        if is_castling_move(move, state):
            if not is_castling_legal(move, state, is_white):
                continue

        # Simulate move
        new_state = state.clone()
        new_state.apply_move(move)
        
        # Check if own king is in check after the move
        king_bb = new_state.pieces.get(king_char, 0)
        if king_bb == 0:
            continue
            
        king_sq = (king_bb & -king_bb).bit_length() - 1
        
        if not is_attacked(king_sq, not is_white, new_state):
            legal_moves.append(move)
            
    return legal_moves
