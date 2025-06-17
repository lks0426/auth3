import React, { useState, useEffect } from 'react';

const ThemeToggle: React.FC = () => {
  const [theme, setTheme] = useState('light'); // Default theme

  // Effect to apply the theme to the document body or a top-level element
  useEffect(() => {
    // Example: document.documentElement.setAttribute('data-theme', theme);
    console.log(`Theme set to ${theme}`);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  return <button onClick={toggleTheme}>Toggle Theme ({theme})</button>;
};

export default ThemeToggle;
