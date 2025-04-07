import React from "react";
import Leaderboard from "./components/Leaderboard";
import './App.css';

function App() {
  return (
    <div className="App">
      <h1 className="container">Google Cloud Arcade Leaderboard</h1>
      <div className="table-wrapper"><Leaderboard /></div>
    </div>
  );
}

export default App;
