import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { SaveGameProvider } from './contexts/SaveGameContext';
import Header from './components/Header';
import ProtectedRoute from './components/ProtectedRoute';
import StoryGenerator from './components/storygenerator';
import StoryLoader from './components/storyloader';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <SaveGameProvider>
        <Router>
          <Header />
          <main className="main-content">
            <Routes>
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <StoryGenerator />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/story/:id"
                element={
                  <ProtectedRoute>
                    <StoryLoader />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                }
              />
            </Routes>
          </main>
        </Router>
      </SaveGameProvider>
    </AuthProvider>
  );
}

export default App;
