// frontend/src/App.js
import React from 'react';
import Simulator from './components/Simulator';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Go-Back-N Protocol Simulator</h1>
      </header>
      <main>
        <Simulator />
      </main>
    </div>
  );
}

export default App;
