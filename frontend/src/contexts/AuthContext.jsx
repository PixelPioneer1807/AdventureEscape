import { createContext, useContext, useReducer, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

const authReducer = (state, action) => {
    switch (action.type) {
        case 'LOGIN_START':
            return { ...state, loading: true, error: null };
        case 'LOGIN_SUCCESS':
            return { 
                ...state, 
                loading: false, 
                isAuthenticated: true, 
                user: action.payload.user,
                token: action.payload.token,
                error: null 
            };
        case 'LOGIN_FAILURE':
            return { 
                ...state, 
                loading: false, 
                isAuthenticated: false, 
                user: null, 
                token: null,
                error: action.payload 
            };
        case 'LOGOUT':
            return { 
                ...state, 
                isAuthenticated: false, 
                user: null, 
                token: null,
                loading: false,
                error: null 
            };
        case 'SET_USER':
            return { 
                ...state, 
                user: action.payload,
                isAuthenticated: true,
                loading: false 
            };
        case 'CLEAR_ERROR':
            return { ...state, error: null };
        default:
            return state;
    }
};

const initialState = {
    isAuthenticated: false,
    user: null,
    token: null,
    loading: false,
    error: null,
};

export const AuthProvider = ({ children }) => {
    const [state, dispatch] = useReducer(authReducer, initialState);

    // Setup axios interceptor for automatic token attachment
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            // Verify token is still valid
            verifyToken(token);
        }
    }, []);

    // Update axios header when token changes
    useEffect(() => {
        if (state.token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${state.token}`;
            localStorage.setItem('token', state.token);
        } else {
            delete axios.defaults.headers.common['Authorization'];
            localStorage.removeItem('token');
        }
    }, [state.token]);

    const verifyToken = async (token) => {
        try {
            const response = await axios.get('/api/auth/me');
            dispatch({ 
                type: 'SET_USER', 
                payload: response.data 
            });
        } catch (error) {
            // Token is invalid, clear it
            logout();
        }
    };

    const register = async (userData) => {
        dispatch({ type: 'LOGIN_START' });
        try {
            const registerResponse = await axios.post('/api/auth/register', userData);
            
            // Auto-login after registration
            const loginResponse = await axios.post('/api/auth/login', {
                email: userData.email,
                password: userData.password
            });

            dispatch({ 
                type: 'LOGIN_SUCCESS', 
                payload: {
                    user: registerResponse.data,
                    token: loginResponse.data.access_token
                }
            });
            return { success: true };
        } catch (error) {
            const errorMessage = error.response?.data?.detail || 'Registration failed';
            dispatch({ 
                type: 'LOGIN_FAILURE', 
                payload: errorMessage 
            });
            return { success: false, error: errorMessage };
        }
    };

    const login = async (credentials) => {
        dispatch({ type: 'LOGIN_START' });
        try {
            const response = await axios.post('/api/auth/login', credentials);
            const token = response.data.access_token;
            
            // Get user info
            const userResponse = await axios.get('/api/auth/me', {
                headers: { Authorization: `Bearer ${token}` }
            });

            dispatch({ 
                type: 'LOGIN_SUCCESS', 
                payload: {
                    user: userResponse.data,
                    token: token
                }
            });
            return { success: true };
        } catch (error) {
            const errorMessage = error.response?.data?.detail || 'Login failed';
            dispatch({ 
                type: 'LOGIN_FAILURE', 
                payload: errorMessage 
            });
            return { success: false, error: errorMessage };
        }
    };

    const logout = () => {
        dispatch({ type: 'LOGOUT' });
    };

    const clearError = () => {
        dispatch({ type: 'CLEAR_ERROR' });
    };

    const value = {
        ...state,
        register,
        login,
        logout,
        clearError,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
