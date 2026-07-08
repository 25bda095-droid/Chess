import { useState } from 'react';
import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';
import Login from './components/Login';
import AIDashboard from './components/AIDashboard';
import ControlPanel from './components/ControlPanel';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [game, setGame] = useState(new Chess());
  const [explanation, setExplanation] = useState('');

  async function onDrop(sourceSquare, targetSquare) {
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
    setGame(gameCopy);
    
    try {
      const response = await fetch('http://localhost:8000/api/move', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ fen: gameCopy.fen() })
      });
      const data = await response.json();
      
      if (data.best_move) {
        const aiGameCopy = new Chess(gameCopy.fen());
        try {
          const moveObj = {
            from: data.best_move.substring(0, 2),
            to: data.best_move.substring(2, 4),
            promotion: data.best_move.length > 4 ? data.best_move.substring(4) : undefined
          };
          const result = aiGameCopy.move(moveObj);
          if (!result) {
            aiGameCopy.move(data.best_move);
          }
        } catch (e) {
          console.error("Move error", e);
        }
        setGame(aiGameCopy);
      }
    } catch (error) {
      console.error('Error fetching AI move:', error);
    }

    return true;
  }

  // Show login screen if no user is set
  if (!user) {
    return <Login onLogin={setUser} />;
  }

  // Main application layout
  return (
    <div className="layout-container">
      <header className="header">
        <h1>Chess AI Coach</h1>
        <div className="user-profile">
          <span className="user-icon">👤</span> {user}
        </div>
      </header>
      
      <div className="main-content">
        <div className="left-sidebar">
          <ControlPanel />
        </div>
        
        <div className="chessboard-container">
          <Chessboard 
            position={game.fen()} 
            onPieceDrop={onDrop} 
            customDarkSquareStyle={{ backgroundColor: '#779556' }}
            customLightSquareStyle={{ backgroundColor: '#ebecd0' }}
          />
        </div>
        
        <div className="right-sidebar">
          <AIDashboard explanation={explanation} />
        </div>
      </div>
    </div>
  );
}

export default App;
