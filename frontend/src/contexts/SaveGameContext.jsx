import { createContext, useContext, useReducer } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';

const SaveGameContext = createContext();

const saveGameReducer = (state, action) => {
    switch (action.type) {
        case 'SET_LOADING':
            return { ...state, loading: action.payload };
        case 'SET_SAVES':
            return { ...state, saves: action.payload, loading: false };
        case 'ADD_SAVE':
            return { ...state, saves: [action.payload, ...state.saves] };
        case 'UPDATE_SAVE':
            return {
                ...state,
                saves: state.saves.map(save => 
                    save.id === action.payload.id ? action.payload : save
                )
            };
        case 'DELETE_SAVE':
            return {
                ...state,
                saves: state.saves.filter(save => save.id !== action.payload)
            };
        case 'SET_ERROR':
            return { ...state, error: action.payload, loading: false };
        case 'CLEAR_ERROR':
            return { ...state, error: null };
        default:
            return state;
    }
};

const initialState = {
    saves: [],
    loading: false,
    error: null,
};

export const SaveGameProvider = ({ children }) => {
    const [state, dispatch] = useReducer(saveGameReducer, initialState);
    const { isAuthenticated } = useAuth();

    const loadUserSaves = async (storyId = null) => {
        if (!isAuthenticated) return;
        
        dispatch({ type: 'SET_LOADING', payload: true });
        try {
            const url = storyId ? `/api/saves/?story_id=${storyId}` : '/api/saves/';
            const response = await axios.get(url);
            dispatch({ type: 'SET_SAVES', payload: response.data });
        } catch (error) {
            dispatch({ type: 'SET_ERROR', payload: 'Failed to load save games' });
        }
    };

    const createSave = async (saveData) => {
        dispatch({ type: 'SET_LOADING', payload: true });
        try {
            const response = await axios.post('/api/saves/', saveData);
            dispatch({ type: 'ADD_SAVE', payload: response.data });
            return { success: true, save: response.data };
        } catch (error) {
            const errorMessage = error.response?.data?.detail || 'Failed to save game';
            dispatch({ type: 'SET_ERROR', payload: errorMessage });
            return { success: false, error: errorMessage };
        }
    };

    const updateSave = async (saveId, saveData) => {
        dispatch({ type: 'SET_LOADING', payload: true });
        try {
            const response = await axios.put(`/api/saves/${saveId}`, saveData);
            dispatch({ type: 'UPDATE_SAVE', payload: response.data });
            return { success: true, save: response.data };
        } catch (error) {
            const errorMessage = error.response?.data?.detail || 'Failed to update save game';
            dispatch({ type: 'SET_ERROR', payload: errorMessage });
            return { success: false, error: errorMessage };
        }
    };

    const deleteSave = async (saveId) => {
        try {
            await axios.delete(`/api/saves/${saveId}`);
            dispatch({ type: 'DELETE_SAVE', payload: saveId });
            return { success: true };
        } catch (error) {
            const errorMessage = error.response?.data?.detail || 'Failed to delete save game';
            dispatch({ type: 'SET_ERROR', payload: errorMessage });
            return { success: false, error: errorMessage };
        }
    };

    const loadSave = async (saveId) => {
        dispatch({ type: 'SET_LOADING', payload: true });
        try {
            const response = await axios.post(`/api/saves/${saveId}/load`);
            dispatch({ type: 'SET_LOADING', payload: false });
            return { success: true, data: response.data };
        } catch (error) {
            const errorMessage = error.response?.data?.detail || 'Failed to load save game';
            dispatch({ type: 'SET_ERROR', payload: errorMessage });
            return { success: false, error: errorMessage };
        }
    };

    const getUserProgress = async () => {
        if (!isAuthenticated) return { success: false };
        
        try {
            const response = await axios.get('/api/saves/progress/stories');
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, error: 'Failed to load progress' };
        }
    };

    const clearError = () => {
        dispatch({ type: 'CLEAR_ERROR' });
    };

    const value = {
        ...state,
        loadUserSaves,
        createSave,
        updateSave,
        deleteSave,
        loadSave,
        getUserProgress,
        clearError,
    };

    return (
        <SaveGameContext.Provider value={value}>
            {children}
        </SaveGameContext.Provider>
    );
};

export const useSaveGame = () => {
    const context = useContext(SaveGameContext);
    if (!context) {
        throw new Error('useSaveGame must be used within a SaveGameProvider');
    }
    return context;
};
