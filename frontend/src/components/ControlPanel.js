// frontend/src/components/ControlPanel.js
import React from 'react';

const ControlPanel = ({ isRunning, onStart, onStop }) => {
  return (
    <div className="control-panel">
      <button 
        className={`control-btn start ${isRunning ? 'disabled' : ''}`}
        onClick={onStart}
        disabled={isRunning}
      >
        Start
      </button>
      <button 
        className={`control-btn stop ${!isRunning ? 'disabled' : ''}`}
        onClick={onStop}
        disabled={!isRunning}
      >
        Stop
      </button>
    </div>
  );
};

export default ControlPanel;
