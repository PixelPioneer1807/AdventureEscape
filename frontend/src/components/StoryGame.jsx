import { useState, useEffect, useCallback } from 'react';
import { logEvent } from '../util/analytics';
import { useSaveGame } from '../contexts/SaveGameContext';
import SaveGameModal from './saves/SaveGameModal';
import LoadGameModal from './saves/LoadGameModal';
import './StoryGame.css';

function StoryGame({ story, onNewStory }) {
  const [nodeId, setNodeId] = useState(null);
  const [node, setNode] = useState(null);
  const [isEnd, setIsEnd] = useState(false);
  const [isWin, setIsWin] = useState(false);
  const [choices, setChoices] = useState([]);
  const [visited, setVisited] = useState([]);
  const [start, setStart] = useState(Date.now());

  const [showSave, setShowSave] = useState(false);
  const [showLoad, setShowLoad] = useState(false);
  const [autoSave, setAutoSave] = useState(true);

  const { createSave } = useSaveGame();

  useEffect(() => {
    if (story?.root_node) {
      const id = story.root_node.id;
      setNodeId(id);
      setVisited([id]);
      setStart(Date.now());
      logEvent({ storyId: story.id, eventType: 'start', payload: {} });
    }
  }, [story]);

  useEffect(() => {
    if (nodeId && story?.all_nodes) {
      const n = story.all_nodes[nodeId];
      setNode(n);
      setIsEnd(n.is_ending);
      setIsWin(n.is_winning_ending);
      if (n.is_ending) {
        logEvent({
          storyId: story.id,
          eventType: 'ending',
          payload: { is_winning_ending: n.is_winning_ending },
        });
      }
    }
  }, [nodeId, story]);

  const autoSaveFn = useCallback(async () => {
    if (!story || !nodeId) return;
    await createSave({
      story_id: story.id,
      current_node_id: nodeId,
      save_name: 'Auto Save',
      choices_made: choices,
      nodes_visited: visited,
      play_time_minutes: Math.floor((Date.now() - start) / 60000),
      is_auto_save: true,
    });
  }, [story, nodeId, choices, visited, start, createSave]);

  useEffect(() => {
    if (!autoSave || isEnd) return;
    const iv = setInterval(autoSaveFn, 30000);
    return () => clearInterval(iv);
  }, [autoSave, isEnd, autoSaveFn]);

  const choose = (nextId, text) => {
    setChoices(prev => [
      ...prev,
      { node_id: nodeId, option_text: text, next_node_id: nextId, timestamp: new Date().toISOString() }
    ]);
    setVisited(prev => [...prev, nextId]);
    logEvent({ storyId: story.id, eventType: 'choice', payload: { from: nodeId, to: nextId, text } });
    setNodeId(nextId);
  };

  const restart = () => {
    const id = story.root_node.id;
    setNodeId(id);
    setChoices([]);
    setVisited([id]);
    setStart(Date.now());
  };

  const runTime = Math.floor((Date.now() - start) / 60000);

  return (
    <div className="story-game">
      <h2>{story.title}</h2>
      <div className="controls">
        <button onClick={() => setShowSave(true)}>💾 Save</button>
        <button onClick={() => setShowLoad(true)}>📁 Load</button>
        <label>
          <input
            type="checkbox"
            checked={autoSave}
            onChange={e => setAutoSave(e.target.checked)}
          />
          Auto Save
        </label>
      </div>

      <div className="progress">
        Visited: {visited.length} • Time: {runTime} min
      </div>

      <div className="content">
        <p>{node?.content}</p>
        {isEnd ? (
          <div className="ending">
            <h3>{isWin ? '🎉 You Win!' : '📖 The End'}</h3>
            <p>Your adventure is over.</p>
            <div className="stats">
              Choices: {choices.length} • Nodes: {visited.length} • Time: {runTime} min
            </div>
          </div>
        ) : (
          <div className="options">
            {node?.options.map((o, i) => (
              <button key={i} onClick={() => choose(o.node_id, o.text)}>
                {o.text}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="footer-buttons">
        <button onClick={restart}>🔄 Restart</button>
        {onNewStory && <button onClick={onNewStory}>✨ New Story</button>}
      </div>

      <SaveGameModal
        isOpen={showSave}
        onClose={() => setShowSave(false)}
        storyId={story.id}
        currentNodeId={nodeId}
        gameState={{ choicesMade: choices, nodesVisited: visited, playTimeMinutes: runTime }}
      />
      <LoadGameModal
        isOpen={showLoad}
        onClose={() => setShowLoad(false)}
        storyId={story.id}
        onLoadComplete={({ save_game }) => {
          setNodeId(save_game.current_node_id);
          setChoices(save_game.choices_made);
          setVisited(save_game.nodes_visited);
          setStart(Date.now() - save_game.play_time_minutes * 60000);
          setShowLoad(false);
        }}
      />
    </div>
  );
}

export default StoryGame;
