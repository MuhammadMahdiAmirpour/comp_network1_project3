// src/index.js
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import { setFavicon } from './favicon';
import './App.css';

setFavicon(); // Set the favicon

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);
