import { useState } from 'react';
import LoginModal from './auth/LoginModal';
import RegisterModal from './auth/RegisterModal';
import './AuthPrompt.css';

function AuthPrompt() {
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  return (
    <>
      <div className="landing">
        <h1>Welcome to Interactive Story Generator</h1>
        <p>Create your own choose-your-own-adventure stories with AI. Save your progress and explore endless possibilities.</p>
        <div className="landing-actions">
          <button className="btn primary" onClick={() => setShowRegister(true)}>
            Get Started
          </button>
          <button className="btn" onClick={() => setShowLogin(true)}>
            Sign In
          </button>
        </div>
      </div>

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

export default AuthPrompt;
