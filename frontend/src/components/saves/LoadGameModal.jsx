import { useState, useEffect } from 'react';
import { useSaveGame } from '../../contexts/SaveGameContext';
import './SaveGameModal.css';

function LoadGameModal({ isOpen, onClose, storyId, onLoadComplete }) {
    const { saves, loadUserSaves, loadSave, deleteSave, loading } = useSaveGame();
    const [selectedSave, setSelectedSave] = useState(null);

    useEffect(() => {
        if (isOpen) {
            loadUserSaves(storyId);
        }
    }, [isOpen, storyId]);

    const handleLoadSave = async () => {
        if (!selectedSave) return;

        const result = await loadSave(selectedSave.id);
        if (result.success && onLoadComplete) {
            onLoadComplete(result.data);
        }
    };

    const handleDeleteSave = async (saveId, e) => {
        e.stopPropagation();
        if (window.confirm('Are you sure you want to delete this save?')) {
            await deleteSave(saveId);
            if (selectedSave?.id === saveId) {
                setSelectedSave(null);
            }
        }
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleString();
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content load-modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Load Game</h2>
                    <button className="close-btn" onClick={onClose}>×</button>
                </div>

                <div className="load-content">
                    {loading ? (
                        <div className="loading-saves">
                            <div className="spinner"></div>
                            <p>Loading saved games...</p>
                        </div>
                    ) : saves.length === 0 ? (
                        <div className="no-saves">
                            <p>No saved games found.</p>
                            <p>Start playing and save your progress to see saves here!</p>
                        </div>
                    ) : (
                        <>
                            <div className="saves-list">
                                {saves.map((save) => (
                                    <div 
                                        key={save.id}
                                        className={`save-item ${selectedSave?.id === save.id ? 'selected' : ''}`}
                                        onClick={() => setSelectedSave(save)}
                                    >
                                        <div className="save-info">
                                            <div className="save-header">
                                                <h4 className="save-name">
                                                    {save.is_auto_save && <span className="auto-badge">AUTO</span>}
                                                    {save.save_name}
                                                </h4>
                                                <button
                                                    className="delete-save-btn"
                                                    onClick={(e) => handleDeleteSave(save.id, e)}
                                                    title="Delete Save"
                                                >
                                                    🗑️
                                                </button>
                                            </div>
                                            <p className="save-story">{save.story_title}</p>
                                            <p className="save-progress">
                                                {save.nodes_visited.length} nodes • {save.play_time_minutes} min
                                            </p>
                                            <p className="save-date">
                                                Saved: {formatDate(save.updated_at || save.created_at)}
                                            </p>
                                            {save.current_node_content && (
                                                <p className="save-preview">
                                                    "{save.current_node_content}"
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <div className="load-actions">
                                <button 
                                    className="cancel-btn"
                                    onClick={onClose}
                                >
                                    Cancel
                                </button>
                                <button 
                                    className="load-btn"
                                    onClick={handleLoadSave}
                                    disabled={!selectedSave || loading}
                                >
                                    {loading ? 'Loading...' : 'Load Selected Save'}
                                </button>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}

export default LoadGameModal;
