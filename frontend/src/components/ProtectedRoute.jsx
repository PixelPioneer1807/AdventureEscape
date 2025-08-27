import { useAuth } from '../contexts/AuthContext';
import AuthPrompt from './AuthPrompt';

function ProtectedRoute({ children }) {
    const { isAuthenticated, loading } = useAuth();

    // Show loading spinner while checking authentication
    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-animation">
                    <div className="spinner"></div>
                </div>
                <p className="loading-info">Loading...</p>
            </div>
        );
    }

    // If not authenticated, show login prompt instead of protected content
    if (!isAuthenticated) {
        return <AuthPrompt />;
    }

    // If authenticated, show the protected content
    return children;
}

export default ProtectedRoute;
