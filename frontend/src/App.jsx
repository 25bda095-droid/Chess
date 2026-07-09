import React, { useState, useEffect, Component } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, Outlet } from 'react-router-dom';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return <div style={{ padding: '2rem', color: 'red' }}><h2>Something went wrong in the application.</h2></div>;
    }
    return this.props.children;
  }
}

import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import AIDashboard from './components/AIDashboard';
import ControlPanel from './components/ControlPanel';
import PuzzleRush from './components/PuzzleRush';
import './App.css';

const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('access_token');
  const isAuthenticated = !!token;
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

// Common Layout for the Dashboard
const DashboardLayout = () => {
  return (
    <div className="layout-container" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header className="header">
        <h1>Chess AI Coach</h1>
        <div className="flex items-center gap-6">
          <nav className="flex gap-4">
             <Link to="/" className="text-gray-300 hover:text-white font-medium transition-colors">Play</Link>
             <Link to="/history" className="text-gray-300 hover:text-white font-medium transition-colors">History</Link>
          </nav>
          <div className="user-profile">
            <span className="user-icon">👤</span> Player
          </div>
        </div>
      </header>
      <div style={{ flexGrow: 1 }}>
        <Outlet />
      </div>
    </div>
  );
};

// The Play View (Chess Game)
const PlayView = ({ game, onDrop, explanation, difficulty, setDifficulty, aggression, setAggression, lastMove, onStartPuzzleRush }) => {
  return (
    <div className="main-content">
      <div className="left-sidebar">
        <ControlPanel difficulty={difficulty} setDifficulty={setDifficulty} aggression={aggression} setAggression={setAggression} onStartPuzzleRush={onStartPuzzleRush} />
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
        <AIDashboard explanation={explanation} currentFen={game.fen()} lastMove={lastMove} />
      </div>
    </div>
  );
};

// Premium History View Component
const HistoryView = () => {
  const [games, setGames] = useState([]);
  
  useEffect(() => {
    const fetchGames = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const token = localStorage.getItem('access_token');
        const res = await fetch(`${apiUrl}/history`, {
           headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
           const data = await res.json();
           setGames(data);
        }
      } catch (err) {
        console.error("Failed to fetch history", err);
      }
    };
    fetchGames();
  }, []);

  return (
    <div className="max-w-6xl mx-auto w-full pt-8 pb-12">
      <div className="flex justify-between items-end mb-10">
        <div>
          <h2 className="text-4xl font-extrabold tracking-tight text-white mb-2">Game History</h2>
          <p className="text-gray-400 text-lg">Review your past matches and analyze your performance.</p>
        </div>
        <Link to="/" className="px-6 py-2.5 bg-gray-800 hover:bg-gray-700 text-white rounded-lg font-medium transition-all border border-gray-700 shadow-lg">
          New Game
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <div className="bg-gray-800/80 p-6 rounded-2xl border border-gray-700 shadow-xl backdrop-blur-sm">
          <h3 className="text-gray-400 text-sm font-bold uppercase tracking-wider mb-2">Total Games</h3>
          <p className="text-4xl font-black text-white">{games.length}</p>
        </div>
        <div className="bg-gray-800/80 p-6 rounded-2xl border border-gray-700 shadow-xl backdrop-blur-sm">
          <h3 className="text-gray-400 text-sm font-bold uppercase tracking-wider mb-2">Win Rate</h3>
          <p className="text-4xl font-black text-emerald-400">{games.length > 0 ? Math.round((games.filter(g => g.result === 'win').length / games.length) * 100) : 0}%</p>
        </div>
        <div className="bg-gray-800/80 p-6 rounded-2xl border border-gray-700 shadow-xl backdrop-blur-sm">
          <h3 className="text-gray-400 text-sm font-bold uppercase tracking-wider mb-2">Avg Accuracy</h3>
          <p className="text-4xl font-black text-blue-400">-</p>
        </div>
      </div>

      <div className="bg-gray-800/90 rounded-2xl shadow-2xl border border-gray-700 overflow-hidden backdrop-blur-md">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-900/50 text-gray-300 border-b border-gray-700">
              <th className="p-6 font-bold text-sm tracking-wider uppercase">Date</th>
              <th className="p-6 font-bold text-sm tracking-wider uppercase">Opponent</th>
              <th className="p-6 font-bold text-sm tracking-wider uppercase">Result</th>
              <th className="p-6 font-bold text-sm tracking-wider uppercase">Accuracy</th>
              <th className="p-6 font-bold text-sm tracking-wider uppercase">Moves</th>
              <th className="p-6 font-bold text-sm tracking-wider uppercase text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700/50">
            {games.map((game) => (
              <tr key={game.id} className="hover:bg-gray-700/30 transition-colors group">
                <td className="p-6 text-gray-300 font-medium">{new Date(game.played_at).toLocaleDateString()}</td>
                <td className="p-6 text-white font-semibold text-lg">{game.opponent_name || 'AI'}</td>
                <td className="p-6">
                  <span className={`px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-wider ${
                    game.result?.toLowerCase() === 'win' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                    game.result?.toLowerCase() === 'loss' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                    'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                  }`}>
                    {game.result}
                  </span>
                </td>
                <td className="p-6 text-blue-400 font-bold text-lg">-</td>
                <td className="p-6 text-gray-400 font-medium">-</td>
                <td className="p-6 text-right">
                  <button className="text-indigo-400 hover:text-indigo-300 font-bold text-sm transition-colors opacity-80 group-hover:opacity-100 flex items-center justify-end gap-2 ml-auto">
                    Analyze <span className="text-lg">→</span>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

function App() {
  const [game, setGame] = useState(new Chess());
  const [explanation, setExplanation] = useState('');
  const [difficulty, setDifficulty] = useState(50); // Added difficulty state
  const [aggression, setAggression] = useState(50); // Added aggression state
  const [lastMove, setLastMove] = useState(''); // Track last move for commentary
  const [isPuzzleRushActive, setIsPuzzleRushActive] = useState(false);

  async function onDrop(sourceSquare, targetSquare) {
    const gameCopy = new Chess(game.fen());
    let move = null;
    try {
      move = gameCopy.move({
        from: sourceSquare,
        to: targetSquare,
        promotion: 'q',
      });
      if (move) {
        setLastMove(move.lan || sourceSquare + targetSquare);
      }
    } catch (e) {
      return false;
    }

    if (move === null) return false;
    setGame(gameCopy);
    
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/move`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          fen: gameCopy.fen(),
          difficulty: difficulty,
          aggression: aggression
        })
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

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
          setLastMove(data.best_move);
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

  return (
    <ErrorBoundary>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected Dashboard Layout */}
          <Route path="/" element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }>
            <Route index element={
              isPuzzleRushActive ? 
              <PuzzleRush onExit={() => setIsPuzzleRushActive(false)} /> :
              <PlayView game={game} onDrop={onDrop} explanation={explanation} difficulty={difficulty} setDifficulty={setDifficulty} aggression={aggression} setAggression={setAggression} lastMove={lastMove} onStartPuzzleRush={() => setIsPuzzleRushActive(true)} />
            } />
            <Route path="history" element={<HistoryView />} />
          </Route>
          
          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
