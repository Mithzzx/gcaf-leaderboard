import React from "react";
import Leaderboard from "./components/Leaderboard";
import './App.css';

function App() {
  return (
    <div className="App">
      <h1 className="container no-hover">Google Cloud Arcade Leaderboard</h1>
      <Leaderboard />
    </div>
  );
}

export default App;
