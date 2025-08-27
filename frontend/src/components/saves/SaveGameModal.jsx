import { useState } from 'react';
import { useSaveGame } from '../../contexts/SaveGameContext';
import './SaveGameModal.css';

function SaveGameModal({ 
    isOpen, 
    onClose, 
    storyId, 
    currentNodeId, 
    gameState, 
    onSaveComplete 
}) {
    const [saveName, setSaveName] = useState('');
    const [isAutoSave, setIsAutoSave] = useState(false);
    const { createSave, loading, error, clearError } = useSaveGame();

    const handleSave = async (e) => {
        e.preventDefault();
        
        if (!saveName.trim() && !isAutoSave) {
            return;
        }

        const saveData = {
            story_id: storyId,
            current_node_id: currentNodeId,
            save_name: isAutoSave ? 'Auto Save' : saveName.trim(),
            choices_made: gameState.choicesMade || [],
            nodes_visited: gameState.nodesVisited || [],
            play_time_minutes: gameState.playTimeMinutes || 0,
            is_auto_save: isAutoSave
        };

        const result = await createSave(saveData);
        if (result.success) {
            setSaveName('');
            setIsAutoSave(false);
            clearError();
            onClose();
            if (onSaveComplete) {
                onSaveComplete(result.save);
            }
        }
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content save-modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Save Game</h2>
                    <button className="close-btn" onClick={onClose}>×</button>
                </div>

                <form onSubmit={handleSave} className="save-form">
                    {error && <div className="error-message">{error}</div>}
                    
                    <div className="form-group">
                        <label htmlFor="saveName">Save Name</label>
                        <input
                            id="saveName"
                            type="text"
                            value={saveName}
                            onChange={(e) => setSaveName(e.target.value)}
                            placeholder="Enter a name for your save"
                            disabled={isAutoSave}
                            required={!isAutoSave}
                        />
                    </div>

                    <div className="form-group checkbox-group">
                        <label className="checkbox-label">
                            <input
                                type="checkbox"
                                checked={isAutoSave}
                                onChange={(e) => setIsAutoSave(e.target.checked)}
                            />
                            <span className="checkmark"></span>
                            Auto Save (overwrites previous auto save)
                        </label>
                    </div>

                    <div className="game-state-preview">
                        <h3>Current Progress</h3>
                        <div className="progress-item">
                            <span className="progress-label">Nodes Visited:</span>
                            <span className="progress-value">{gameState.nodesVisited?.length || 0}</span>
                        </div>
                        <div className="progress-item">
                            <span className="progress-label">Play Time:</span>
                            <span className="progress-value">{gameState.playTimeMinutes || 0} minutes</span>
                        </div>
                    </div>

                    <div className="form-actions">
                        <button 
                            type="button" 
                            className="cancel-btn"
                            onClick={onClose}
                        >
                            Cancel
                        </button>
                        <button 
                            type="submit" 
                            className="save-btn"
                            disabled={loading || (!saveName.trim() && !isAutoSave)}
                        >
                            {loading ? 'Saving...' : 'Save Game'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default SaveGameModal;
