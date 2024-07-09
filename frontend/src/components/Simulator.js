import React, { useState, useEffect } from 'react';
import ControlPanel from './ControlPanel';
import LogDisplay from './LogDisplay';

function Simulator() {
  const [transmitterRunning, setTransmitterRunning] = useState(false);
  const [receiverRunning, setReceiverRunning] = useState(false);
  const [transmitterLogs, setTransmitterLogs] = useState([]);
  const [receiverLogs, setReceiverLogs] = useState([]);

  useEffect(() => {
    const interval = setInterval(fetchLogs, 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchLogs = async () => {
    try {
      const response = await fetch('/get_logs/');
      const data = await response.json();
      setTransmitterLogs(prevLogs => [...prevLogs, ...data.transmitter_logs]);
      setReceiverLogs(prevLogs => [...prevLogs, ...data.receiver_logs]);
    } catch (error) {
      console.error('Error fetching logs:', error);
    }
  };

  const handleStart = async (component) => {
    try {
      const response = await fetch(`/start_${component}/`, { method: 'POST' });
      const data = await response.json();
      if (data.status.includes('started')) {
        if (component === 'transmitter') setTransmitterRunning(true);
        if (component === 'receiver') setReceiverRunning(true);
      }
    } catch (error) {
      console.error(`Error starting ${component}:`, error);
    }
  };

  const handleStop = async (component) => {
    try {
      const response = await fetch(`/stop_${component}/`, { method: 'POST' });
      const data = await response.json();
      if (data.status.includes('stopped')) {
        if (component === 'transmitter') setTransmitterRunning(false);
        if (component === 'receiver') setReceiverRunning(false);
      }
    } catch (error) {
      console.error(`Error stopping ${component}:`, error);
    }
  };

  const handleClearLogs = async () => {
    try {
      await fetch('/clear_logs/', { method: 'POST' });
      setTransmitterLogs([]);
      setReceiverLogs([]);
    } catch (error) {
      console.error('Error clearing logs:', error);
    }
  };

  return (
    <div className="simulator">
      <div className="simulator-column">
        <h2>Transmitter</h2>
        <ControlPanel
          isRunning={transmitterRunning}
          onStart={() => handleStart('transmitter')}
          onStop={() => handleStop('transmitter')}
        />
        <LogDisplay logs={transmitterLogs} />
      </div>
      <div className="simulator-column">
        <h2>Receiver</h2>
        <ControlPanel
          isRunning={receiverRunning}
          onStart={() => handleStart('receiver')}
          onStop={() => handleStop('receiver')}
        />
        <LogDisplay logs={receiverLogs} />
      </div>
      <button className="clear-logs-btn" onClick={handleClearLogs}>Clear Logs</button>
    </div>
  );
}

export default Simulator;
