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

  function makeAMove(move) {
    const gameCopy = new Chess(game.fen());
    try {
      const result = gameCopy.move(move);
      setGame(gameCopy);
      return result;
    } catch (e) {
      return null;
    }
  }

  function onDrop(sourceSquare, targetSquare) {
    const move = makeAMove({
      from: sourceSquare,
      to: targetSquare,
      promotion: 'q',
    });

    if (move === null) return false;
    
    // Mocking an AI response for demonstration
    setTimeout(() => {
      setExplanation(`You moved ${move.san}. The AI evaluates this as a solid developmental move. A common alternative here would be placing the knight more centrally.`);
    }, 500);

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
