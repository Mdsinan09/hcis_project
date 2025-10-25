import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import Detector from './pages/Detector';
import Chatbot from './pages/Chatbot';
import Generator from './pages/Generator';
import History from './pages/History';
import './index.css';

const navItems = [
  { path: '/', label: 'Detector', icon: '🔍' },
  { path: '/chatbot', label: 'Chatbot', icon: '💬' },
  { path: '/generator', label: 'Generator', icon: '🧪' },
  { path: '/history', label: 'History', icon: '📊' },
];

const GlassThemeToggle = ({ isMobile }) => {
  const { theme, toggleTheme } = useTheme();
  return (
    <div className={`glass-toggle-container ${isMobile ? 'mobile' : ''}`}>
      <label className="glass-switch">
        <input 
          type="checkbox" 
          checked={theme === 'dark'} 
          onChange={toggleTheme} 
        />
        <span className="glass-switch-slider">
          {theme === 'light' ? '☀️' : '🌙'}
        </span>
        <span className="glass-switch-icon light-label"></span>
        <span className="glass-switch-icon dark-label"></span>
      </label>
    </div>
  );
};

const Sidebar = ({ isSidebarOpen, toggleSidebar }) => {
  const location = useLocation();

  return (
    <div className={`sidebar ${isSidebarOpen ? 'open' : 'closed'}`}>
      <button className="sidebar-close-btn" onClick={toggleSidebar}>
        &times;
      </button> 
      <h1 className="app-title">Navigation</h1> 
      <hr style={{ borderTop: '1px solid rgba(255, 255, 255, 0.1)' }} />
      <GlassThemeToggle />
      <hr style={{ borderTop: '1px solid rgba(255, 255, 255, 0.1)', marginTop: '30px' }} />
      <div className="nav-container">
        {navItems.map(item => (
          <Link
            key={item.path}
            to={item.path}
            className={`nav-button ${location.pathname === item.path ? 'active' : ''}`}
            onClick={window.innerWidth <= 768 ? toggleSidebar : undefined}
          >
            {item.icon} {item.label}
          </Link>
        ))}
      </div>
    </div>
  );
};

const MobileBubbleMenu = () => {
  const location = useLocation();
  if (typeof window !== 'undefined' && window.innerWidth > 768) return null;

  return (
    <div className="mobile-bubble-menu">
      {navItems.map(item => (
        <Link 
          key={item.path} 
          to={item.path} 
          className={`bubble-item ${location.pathname === item.path ? 'active' : ''}`}
        >
          <span>{item.icon}</span>
          {item.label}
        </Link>
      ))}
    </div>
  );
};

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false); 

  const toggleSidebar = () => {
    setIsSidebarOpen(prev => !prev);
  };
  
  useEffect(() => {
    if (isSidebarOpen && window.innerWidth <= 768) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }
  }, [isSidebarOpen]);

  return (
    <div className="app-layout">
      <div 
        className={`sidebar-toggle-btn ${isSidebarOpen ? 'active' : ''}`} 
        onClick={toggleSidebar}
        title="Toggle Navigation"
      >
        <div className="hamburger-line"></div>
        <div className="hamburger-line"></div>
        <div className="hamburger-line"></div>
      </div>

      <GlassThemeToggle isMobile={true} />

      <Sidebar isSidebarOpen={isSidebarOpen} toggleSidebar={toggleSidebar} />
      
      <div className={`main-content ${isSidebarOpen ? 'sidebar-is-open' : ''}`}> 
        <div className="content-container">
          <Routes>
            <Route path="/" element={<Detector />} />
            <Route path="/chatbot" element={<Chatbot />} />
            <Route path="/generator" element={<Generator />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </div>
      </div>

      <MobileBubbleMenu />
    </div>
  );
}

export default function AppWrapper() {
  return (
    <ThemeProvider>
      <Router>
        <App />
      </Router>
    </ThemeProvider>
  );
}