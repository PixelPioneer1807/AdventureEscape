import { useState, useEffect } from 'react';
import axios from 'axios';
import './Dashboard.css';

function Dashboard() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    axios.get('/api/analytics/summary')
      .then(res => setSummary(res.data))
      .catch(err => console.error(err));
  }, []);

  if (!summary) return <p>Loading analytics...</p>;

  return (
    <div className="dashboard">
      <h2>Game Analytics</h2>
      <div className="metrics">
        <div className="metric">
          <h3>{summary.total_starts}</h3>
          <p>Stories Started</p>
        </div>
        <div className="metric">
          <h3>{summary.total_choices}</h3>
          <p>Choices Made</p>
        </div>
        <div className="metric">
          <h3>{summary.completion_rate}%</h3>
          <p>Completion Rate</p>
        </div>
        <div className="metric">
          <h3>{summary.winning_rate}%</h3>
          <p>Winning Rate</p>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
