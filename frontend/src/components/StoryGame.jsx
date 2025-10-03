import React, { useState, useEffect } from 'react';

const StoryGame = ({ storyId }) => {
  const [currentNode, setCurrentNode] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (storyId) {
      fetchStoryNode(storyId);
    }
  }, [storyId]);

  const fetchStoryNode = async (nodeId = null) => {
    try {
      setLoading(true);
      const url = nodeId 
        ? `http://localhost:8000/api/stories/${storyId}/node/${nodeId}`
        : `http://localhost:8000/api/stories/${storyId}/complete`;
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch story data');
      }

      const data = await response.json();
      console.log('Fetched story data:', data); // DEBUG
      
      // If fetching complete story, get the root node
      if (!nodeId && data.nodes) {
        const rootNode = data.nodes.find(node => node.is_root);
        console.log('Found root node:', rootNode); // DEBUG
        setCurrentNode(rootNode);
      } else {
        setCurrentNode(data);
      }
      
      setError(null);
    } catch (err) {
      console.error('Error fetching story:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChoice = (choice) => {
    if (choice.node_id) {
      // Navigate to the next node
      fetchStoryNode(choice.node_id);
    }
  };

  const constructImageUrl = (imagePath) => {
    if (!imagePath) return null;
    
    // Handle different image path formats
    if (imagePath.startsWith('http')) {
      return imagePath; // External URL (placeholder images)
    }
    
    if (imagePath.startsWith('/static/')) {
      // Local images - construct full URL
      return `http://localhost:8000${imagePath}`;
    }
    
    // Fallback for malformed paths
    return `http://localhost:8000/static/${imagePath}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      </div>
    );
  }

  if (!currentNode) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-500">No story node found</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        
        {/* Story Content */}
        <div className="p-6">
          <div className="prose max-w-none">
            <p className="text-lg leading-relaxed text-gray-800 mb-6">
              {currentNode.content}
            </p>
          </div>
        </div>

        {/* Images Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-6 bg-gray-50">
          {/* Image 1 */}
          {currentNode.image_prompt_1 && (
            <div className="space-y-2">
              <img
                src={constructImageUrl(currentNode.image_prompt_1)}
                alt="Story scene 1"
                className="w-full h-64 object-cover rounded-lg shadow-md"
                onError={(e) => {
                  console.error('Failed to load image 1:', currentNode.image_prompt_1);
                  console.error('Constructed URL:', constructImageUrl(currentNode.image_prompt_1));
                  e.target.src = 'https://via.placeholder.com/400x300/cccccc/666666?text=Image+Not+Found';
                }}
                onLoad={() => {
                  console.log('Successfully loaded image 1:', currentNode.image_prompt_1);
                  console.log('Loaded from URL:', constructImageUrl(currentNode.image_prompt_1));
                }}
              />
            </div>
          )}

          {/* Image 2 */}
          {currentNode.image_prompt_2 && (
            <div className="space-y-2">
              <img
                src={constructImageUrl(currentNode.image_prompt_2)}
                alt="Story scene 2"
                className="w-full h-64 object-cover rounded-lg shadow-md"
                onError={(e) => {
                  console.error('Failed to load image 2:', currentNode.image_prompt_2);
                  console.error('Constructed URL:', constructImageUrl(currentNode.image_prompt_2));
                  e.target.src = 'https://via.placeholder.com/400x300/cccccc/666666?text=Image+Not+Found';
                }}
                onLoad={() => {
                  console.log('Successfully loaded image 2:', currentNode.image_prompt_2);
                  console.log('Loaded from URL:', constructImageUrl(currentNode.image_prompt_2));
                }}
              />
            </div>
          )}
        </div>

        {/* Choices Section */}
        {currentNode.options && currentNode.options.length > 0 && (
          <div className="p-6 border-t bg-white">
            <h3 className="text-lg font-semibent text-gray-800 mb-4">
              What do you choose?
            </h3>
            <div className="space-y-3">
              {currentNode.options.map((choice, index) => (
                <button
                  key={index}
                  onClick={() => handleChoice(choice)}
                  className="w-full text-left p-4 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors duration-200 hover:shadow-md"
                >
                  <span className="text-blue-800 font-medium">
                    {choice.text}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Ending Section */}
        {currentNode.is_ending && (
          <div className="p-6 border-t bg-gray-50">
            <div className={`text-center p-4 rounded-lg ${
              currentNode.is_winning_ending 
                ? 'bg-green-100 text-green-800 border border-green-200' 
                : 'bg-red-100 text-red-800 border border-red-200'
            }`}>
              <h3 className="text-xl font-bold mb-2">
                {currentNode.is_winning_ending ? '🎉 Victory!' : '💀 The End'}
              </h3>
              <p>
                {currentNode.is_winning_ending 
                  ? 'Congratulations! You have successfully completed the adventure.' 
                  : 'Your adventure ends here. Would you like to try again?'}
              </p>
            </div>
          </div>
        )}

      </div>

      {/* Debug Information - ALWAYS SHOW FOR NOW */}
      <div className="mt-4 p-4 bg-gray-100 rounded text-xs text-gray-600">
        <strong>Debug Info:</strong>
        <br />Story ID: {storyId}
        <br />Node ID: {currentNode?.id}
        <br />Image 1 Path: {currentNode?.image_prompt_1}
        <br />Image 2 Path: {currentNode?.image_prompt_2}
        <br />Image 1 Full URL: {constructImageUrl(currentNode?.image_prompt_1)}
        <br />Image 2 Full URL: {constructImageUrl(currentNode?.image_prompt_2)}
        <br />Is Root: {currentNode?.is_root ? 'Yes' : 'No'}
        <br />Is Ending: {currentNode?.is_ending ? 'Yes' : 'No'}
        <br />Options Count: {currentNode?.options ? currentNode.options.length : 0}
      </div>
    </div>
  );
};

export default StoryGame;