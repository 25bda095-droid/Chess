import React, { useState, useEffect, useRef } from 'react';
import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';
import './Dashboard.css';

export default function PuzzleRush({ onExit }) {
  const [puzzle, setPuzzle] = useState(null);
  const [game, setGame] = useState(new Chess());
  const [moveIndex, setMoveIndex] = useState(0);
  const [strikes, setStrikes] = useState(0);
  const [score, setScore] = useState(0);
  const [status, setStatus] = useState('loading'); // loading, playing, gameover
  const timeoutRefs = useRef([]);
  
  useEffect(() => {
    return () => {
      timeoutRefs.current.forEach(clearTimeout);
    };
  }, []);
  
  const fetchPuzzle = async () => {
    try {
      setStatus('loading');
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/api/puzzles/random`);
      const data = await res.json();
      setPuzzle(data);
      setGame(new Chess(data.fen));
      setMoveIndex(0);
      setStatus('playing');
    } catch (err) {
      console.error(err);
      setStatus('error');
    }
  };

  useEffect(() => {
    fetchPuzzle();
  }, []);

  const onDrop = (sourceSquare, targetSquare) => {
    if (status !== 'playing') return false;

    const gameCopy = new Chess(game.fen());
    let move = null;
    try {
      move = gameCopy.move({
        from: sourceSquare,
        to: targetSquare,
        promotion: 'q',
      });
    } catch (e) {
      return false;
    }

    if (move === null) return false;

    const expectedMove = puzzle.solution[moveIndex];
    const isCorrect = move.lan === expectedMove || move.lan + 'q' === expectedMove || move.lan.startsWith(expectedMove) || (move.from + move.to) === expectedMove || (move.from + move.to + 'q') === expectedMove;
    
    if (isCorrect) {
      setGame(gameCopy);
      if (moveIndex + 1 >= puzzle.solution.length) {
        // Solved
        setScore(s => s + 1);
        const tid = setTimeout(fetchPuzzle, 1000); // Load next puzzle after 1s
        timeoutRefs.current.push(tid);
      } else {
        // Wait, normally puzzles have opponent moves too.
        // For our MVP, solution is just a list of moves from the user. Or maybe alternate?
        // Our backend puzzle solutions are just 1-3 moves for the same player?
        // Wait! Typical puzzle solutions contain both user and opponent moves!
        // The ones I added: e1e8 (1 move), b1b8, c2c8, b8c8 (3 moves).
        // If it's the user's turn, then opponent's turn, then user's turn.
        setMoveIndex(moveIndex + 1);
        
        // Wait, if it's the opponent's turn now, make the move automatically.
        if ((moveIndex + 1) < puzzle.solution.length) {
           const tid2 = setTimeout(() => {
              const oppGame = new Chess(gameCopy.fen());
              const oppMoveUci = puzzle.solution[moveIndex + 1];
              try {
                oppGame.move({
                  from: oppMoveUci.substring(0, 2),
                  to: oppMoveUci.substring(2, 4),
                  promotion: oppMoveUci.length > 4 ? oppMoveUci.substring(4) : 'q'
                });
                setGame(oppGame);
                setMoveIndex(moveIndex + 2);
              } catch(e) {
                console.error("Opponent move failed", e);
              }
           }, 500);
           timeoutRefs.current.push(tid2);
        }
      }
      return true;
    } else {
      // Wrong move
      setStrikes(s => s + 1);
      if (strikes + 1 >= 3) {
        setStatus('gameover');
      } else {
        // Let them try again
        // don't update game state
      }
      return false;
    }
  };

  return (
    <div className="main-content" style={{ display: 'flex', gap: '2rem', padding: '2rem' }}>
      <div className="left-sidebar" style={{ flex: 1 }}>
        <div className="panel control-panel">
          <h2>⚡ Puzzle Rush</h2>
          <div style={{ marginTop: '1rem', fontSize: '1.2rem' }}>
            <p>Score: <strong>{score}</strong></p>
            <p>Strikes: <strong>{'❌'.repeat(strikes)}{'⭕'.repeat(3 - strikes)}</strong></p>
          </div>
          {status === 'gameover' && (
            <div style={{ marginTop: '2rem' }}>
              <h3 style={{ color: '#ff4444' }}>Game Over!</h3>
              <button 
                onClick={() => { setScore(0); setStrikes(0); fetchPuzzle(); }}
                style={{ padding: '0.5rem 1rem', marginTop: '1rem', cursor: 'pointer', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '4px' }}
              >
                Try Again
              </button>
            </div>
          )}
          <button 
            onClick={onExit}
            style={{ padding: '0.5rem 1rem', marginTop: '1rem', cursor: 'pointer', background: '#4b5563', color: 'white', border: 'none', borderRadius: '4px', width: '100%' }}
          >
            Exit Puzzle Rush
          </button>
        </div>
      </div>
      
      <div className="chessboard-container" style={{ flex: 2 }}>
        <Chessboard 
          position={game.fen()} 
          onPieceDrop={onDrop}
          customDarkSquareStyle={{ backgroundColor: '#779556' }}
          customLightSquareStyle={{ backgroundColor: '#ebecd0' }}
          boardOrientation={puzzle ? (puzzle.fen.split(' ')[1] === 'w' ? 'white' : 'black') : 'white'}
        />
      </div>
    </div>
  );
}
