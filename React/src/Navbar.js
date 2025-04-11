import React from 'react';
import './css/Navbar.css';

const Navbar = () => {
  const clearAllLocalStorage = () => {
    localStorage.clear();
  };

  return (

<nav className="navbar">
  <div className="navbar-center">
    <a href="/" className="logo" onClick={clearAllLocalStorage}>
        Swedew Valley Marketplace
    </a>
  </div>
</nav>
);
};

export default Navbar;