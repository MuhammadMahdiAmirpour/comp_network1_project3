// src/favicon.js
import favicon from './icon.svg'; // or './icon.svg' if you prefer

export const setFavicon = () => {
  const link = document.querySelector("link[rel*='icon']") || document.createElement('link');
  link.type = 'image/png'; // or 'image/svg+xml' for SVG
  link.rel = 'shortcut icon';
  link.href = favicon;
  document.getElementsByTagName('head')[0].appendChild(link);
};
