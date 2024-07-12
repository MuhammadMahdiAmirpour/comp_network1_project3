import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ControlPanel from './ControlPanel';
import LogDisplay from './LogDisplay';

// Configure axios to include CSRF token
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

const Simulator = () => {
  const [transmitterRunning, setTransmitterRunning] = useState(false);
  const [receiverRunning, setReceiverRunning] = useState(false);
  const [transmitterLogs, setTransmitterLogs] = useState([]);
  const [receiverLogs, setReceiverLogs] = useState([]);
  const [encoding, setEncoding] = useState('PARITY');
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDataAndStatus = async () => {
      await fetchStatus();
      await fetchLogs();
    };

    fetchDataAndStatus();
    const interval = setInterval(fetchDataAndStatus, 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await axios.get('/get_status/');
      console.log('Status response:', response.data);
      setTransmitterRunning(response.data.transmitter_status === 'running');
      setReceiverRunning(response.data.receiver_status === 'running');
      setError(null);
    } catch (error) {
      console.error('Error fetching status:', error);
      setError('Failed to fetch status. Please check your connection.');
    }
  };

  const fetchLogs = async () => {
    try {
      const response = await axios.get('/get_logs/');
      console.log('Logs response:', response.data);
      setTransmitterLogs(response.data.transmitter_logs);
      setReceiverLogs(response.data.receiver_logs);
    } catch (error) {
      console.error('Error fetching logs:', error);
    }
  };

  const handleStart = async (type) => {
    try {
      if (type === 'transmitter') {
        await axios.post('/start_transmitter/');
      } else if (type === 'receiver') {
        await axios.post('/start_receiver/');
      }
      await fetchStatus();
      setError(null);
    } catch (error) {
      console.error(`Error starting ${type}:`, error);
      setError(`Failed to start ${type}. Please try again.`);
    }
  };

  const handleStop = async (type) => {
    try {
      if (type === 'transmitter') {
        await axios.post('/stop_transmitter/');
      } else if (type === 'receiver') {
        await axios.post('/stop_receiver/');
      }
      await fetchStatus();
      setError(null);
    } catch (error) {
      console.error(`Error stopping ${type}:`, error);
      setError(`Failed to stop ${type}. Please try again.`);
    }
  };

  const handleEncodingChange = async (method) => {
    try {
      await axios.post('/set_encoding/', { encoding: method });
      setEncoding(method);
      setError(null);
    } catch (error) {
      console.error('Error setting encoding:', error);
      setError('Failed to set encoding. Please try again.');
    }
  };

  const handleClearLogs = async () => {
    try {
      await axios.post('/clear_logs/');
      setTransmitterLogs([]);
      setReceiverLogs([]);
      setError(null);
    } catch (error) {
      console.error('Error clearing logs:', error);
      setError('Failed to clear logs. Please try again.');
    }
  };

  return (
    <div className="simulator">
      {error && <div className="error-message">{error}</div>}
      <div className="simulator-row">
        <div className="simulator-column">
          <h2>Transmitter</h2>
          <ControlPanel
            isRunning={transmitterRunning}
            onStart={() => handleStart('transmitter')}
            onStop={() => handleStop('transmitter')}
          />
          <LogDisplay logs={transmitterLogs} />
          <div>Transmitter status: {transmitterRunning ? 'Running' : 'Stopped'}</div>
        </div>
        <div className="simulator-column">
          <h2>Receiver</h2>
          <ControlPanel
            isRunning={receiverRunning}
            onStart={() => handleStart('receiver')}
            onStop={() => handleStop('receiver')}
          />
          <LogDisplay logs={receiverLogs} />
          <div>Receiver status: {receiverRunning ? 'Running' : 'Stopped'}</div>
        </div>
      </div>
      <div className="encoding-section">
        <h3>Select Encoding Method:</h3>
        <div className="btn-group" role="group" aria-label="Encoding selection">
          {['PARITY', 'TWO_D_PARITY', 'HAMMING', 'CHECKSUM'].map((method) => (
            <button
              key={method}
              type="button"
              className={`btn ${encoding === method ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => handleEncodingChange(method)}
            >
              {method.replace('_', ' ')}
            </button>
          ))}
        </div>
        <button className="clear-logs-btn" onClick={handleClearLogs}>Clear Logs</button>
      </div>
    </div>
  );
};

export default Simulator;
