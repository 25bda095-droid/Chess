import React, { useState } from 'react';
import './Dashboard.css';

export default function ControlPanel({ difficulty, setDifficulty, aggression, setAggression, onStartPuzzleRush }) {

  const getDifficultyLabel = (val) => {
    if (val < 20) return "Easy 🟢";
    if (val < 40) return "Medium 🟡";
    if (val < 60) return "Hard 🟠";
    if (val < 80) return "Expert 🔴";
    return "Grandmaster 🟣";
  };

  const getAggressionLabel = (val) => {
    if (val < 20) return "Defensive 🛡️";
    if (val < 40) return "Solid 🧱";
    if (val < 60) return "Balanced ⚖️";
    if (val < 80) return "Aggressive 🗡️";
    return "Berserk 🩸";
  };

  return (
    <div className="panel control-panel">
      <h3>⚙️ Engine Settings</h3>
      
      <div className="slider-group">
        <div className="slider-header">
          <label>Difficulty Level</label>
          <span className="slider-value">{getDifficultyLabel(difficulty)}</span>
        </div>
        <input 
          type="range" 
          min="0" max="100" 
          value={difficulty} 
          onChange={(e) => setDifficulty(parseInt(e.target.value))}
        />
        <div className="slider-marks">
          <span>Easy</span>
          <span>Med</span>
          <span>Hard</span>
          <span>Expert</span>
          <span>GM</span>
        </div>
      </div>
      
      <div className="slider-group" style={{ marginTop: '1.5rem' }}>
        <div className="slider-header">
          <label>Aggression Bias</label>
          <span className="slider-value">{getAggressionLabel(aggression)}</span>
        </div>
        <input 
          type="range" 
          min="0" max="100" 
          value={aggression}
          onChange={(e) => setAggression(parseInt(e.target.value))}
        />
      </div>

      <div style={{ marginTop: '2rem' }}>
        <button 
          onClick={onStartPuzzleRush}
          style={{ padding: '0.75rem', width: '100%', background: '#8b5cf6', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', fontSize: '1rem' }}
        >
          ⚡ Start Puzzle Rush
        </button>
      </div>
    </div>
  );
}
