import React, { useState } from 'react';
import './Dashboard.css';

export default function ControlPanel() {
  const [difficulty, setDifficulty] = useState(10);
  const [aggression, setAggression] = useState(5);

  const getDifficultyLabel = (val) => {
    if (val < 5) return "Easy 🟢";
    if (val < 9) return "Medium 🟡";
    if (val < 13) return "Hard 🟠";
    if (val < 17) return "Expert 🔴";
    return "Grandmaster 🟣";
  };

  const getAggressionLabel = (val) => {
    if (val < 4) return "Passive 🛡️";
    if (val < 8) return "Balanced ⚖️";
    return "Aggressive ⚔️";
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
          min="1" max="20" 
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
          min="1" max="10" 
          value={aggression}
          onChange={(e) => setAggression(parseInt(e.target.value))}
        />
      </div>
      
      <div className="divider"></div>
      
      <h3>🧩 Training</h3>
      <p className="training-text">Based on your mistake history</p>
      <button className="puzzle-rush-btn">⚡ Start Puzzle Rush</button>
    </div>
  );
}
