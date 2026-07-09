import React, { useState, useEffect, useRef } from 'react';
import './Dashboard.css';

export default function AIDashboard({ explanation, currentFen, lastMove }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioUrlRef = useRef(null);
  
  useEffect(() => {
    return () => {
      if (audioUrlRef.current) {
        URL.revokeObjectURL(audioUrlRef.current);
      }
    };
  }, []);

  const playHindiCommentary = async () => {
    if (!currentFen || !lastMove) return;
    try {
      setIsPlaying(true);
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/commentary/hindi?fen=${encodeURIComponent(currentFen)}&move=${encodeURIComponent(lastMove)}`);
      
      if (!response.ok) throw new Error("Failed to get audio");
      
      const blob = await response.blob();
      if (audioUrlRef.current) {
        URL.revokeObjectURL(audioUrlRef.current);
      }
      const audioUrl = URL.createObjectURL(blob);
      audioUrlRef.current = audioUrl;
      const audio = new Audio(audioUrl);
      
      audio.onended = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(audioUrl);
        audioUrlRef.current = null;
      };
      audio.play();
    } catch (e) {
      console.error(e);
      setIsPlaying(false);
    }
  };

  return (
    <div className="panel ai-dashboard">
      <h3>🤖 AI Coach</h3>
      <div className="explanation-box">
        {explanation ? (
          <p>{explanation}</p>
        ) : (
          <p className="placeholder">Make a move to get AI feedback...</p>
        )}
      </div>
      <button 
        onClick={playHindiCommentary} 
        disabled={isPlaying || !lastMove}
        style={{ marginTop: '1rem', padding: '0.5rem 1rem', background: '#eab308', color: '#1a1a1a', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', width: '100%' }}
      >
        {isPlaying ? '🔊 Playing...' : '🎙️ Play Hindi Commentary'}
      </button>
    </div>
  );
}
