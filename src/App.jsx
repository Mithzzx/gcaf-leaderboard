import { useState, useEffect } from "react";
import Leaderboard from "./components/Leaderboard";
import './App.css';

// API base URL - we'll set this to the Render deployment URL
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

function App() {
  const [hasBackend, setHasBackend] = useState(false);

  useEffect(() => {
    // Function to ping the backend to keep it alive
    const pingBackend = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        setHasBackend(response.ok);
        console.log("Keep-alive ping:", response.ok ? "success" : "failed");
      } catch (error) {
        console.log("Keep-alive ping failed:", error);
        setHasBackend(false);
      }
    };

    // Ping immediately when the app loads
    pingBackend();

    // Set up interval to ping every 10 minutes (600000 ms)
    const intervalId = setInterval(pingBackend, 600000);

    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="App">
      <h1 className="container no-hover">Google Cloud Arcade Festival Leaderboard</h1>
      <Leaderboard backendAvailable={hasBackend} />
    </div>
  );
}

export default App;
