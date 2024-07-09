// frontend/src/components/LogDisplay.js
import React, { useRef, useEffect } from 'react';

function LogDisplay({ logs }) {
  const logEndRef = useRef(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div className="log-display">
      {logs.map((log, index) => (
        <p key={index} className="log-entry">{log}</p>
      ))}
      <div ref={logEndRef} />
    </div>
  );
}

export default LogDisplay;
