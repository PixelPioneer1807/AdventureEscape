import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LoginModal from './auth/LoginModal';
import RegisterModal from './auth/RegisterModal';
import './Header.css';

function Header() {
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  return (
    <>
      <header className="app-header">
        <div className="header-inner">
          <h1 onClick={() => navigate('/')} className="logo">
            Interactive Story Generator
          </h1>
          <nav className="nav-actions">
            {isAuthenticated ? (
              <>
                <button className="btn nav-btn" onClick={() => navigate('/')}>
                  Home
                </button>
                <button className="btn nav-btn" onClick={() => navigate('/dashboard')}>
                  Dashboard
                </button>
                <span className="welcome-text">Hello, {user.username}</span>
                <button className="btn logout-btn" onClick={logout}>
                  Logout
                </button>
              </>
            ) : (
              <>
                <button className="btn nav-btn" onClick={() => setShowLogin(true)}>
                  Sign In
                </button>
                <button className="btn nav-btn primary" onClick={() => setShowRegister(true)}>
                  Sign Up
                </button>
              </>
            )}
          </nav>
        </div>
      </header>

      <LoginModal
        isOpen={showLogin}
        onClose={() => setShowLogin(false)}
        onSwitchToRegister={() => {
          setShowLogin(false);
          setShowRegister(true);
        }}
      />
      <RegisterModal
        isOpen={showRegister}
        onClose={() => setShowRegister(false)}
        onSwitchToLogin={() => {
          setShowRegister(false);
          setShowLogin(true);
        }}
      />
    </>
  );
}

export default Header;
