import React from 'react';
import './Dashboard.css';

export default function AIDashboard({ explanation }) {
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
      <button className="play-audio-btn">🔊 Play Hindi Commentary</button>
    </div>
  );
}
