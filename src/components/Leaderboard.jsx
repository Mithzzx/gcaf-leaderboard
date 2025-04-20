import React, { useEffect, useState, useMemo, useCallback } from "react";
import Papa from "papaparse";
import ReactConfetti from "react-confetti";

// API base URL - we'll set this to the Render deployment URL
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

export default function Leaderboard() {
  const [participants, setParticipants] = useState([]);
  const [selectedParticipant, setSelectedParticipant] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [windowDimensions, setWindowDimensions] = useState({
    width: window.innerWidth,
    height: window.innerHeight
  });

  useEffect(() => {
    let timeoutId = null;
    const handleResize = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        setWindowDimensions({
          width: window.innerWidth,
          height: window.innerHeight
        });
      }, 100);
    };
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      clearTimeout(timeoutId);
    };
  }, []);

  const loadData = useCallback(async (abortController) => {
    setIsLoading(true);
    try {
      // First try to load from the API
      let response;
      try {
        response = await fetch(`${API_BASE_URL}/api/leaderboard`, { 
          signal: abortController.signal 
        });
        
        if (response.ok) {
          const jsonData = await response.json();
          setLastUpdated(new Date());
          
          const processedData = jsonData.map((row) => ({
            name: row["name"] || "Unknown",
            arcade: parseInt(row["game_badges"]) || 0,
            specialArcade: parseInt(row["special_game_badges"]) || 0,
            trivia: parseInt(row["trivia_badges"]) || 0,
            skill: parseInt(row["skill_badges"]) || 0,
            labs: parseInt(row["lab_badges"]) || 0,
            score: parseInt(row["total_points"]) || 0,
            milestone: row["milestone"] || "None",
          }));

          const validData = processedData.filter(p => !isNaN(p.score));
          setParticipants(validData);
          setIsLoading(false);
          return;
        }
      } catch (e) {
        console.log(`Failed to load from API: ${e.message}`);
      }
      
      // Fallback to local CSV files if API fails
      const dataSources = [
        "/profiles_data.csv",
        "/data/profiles/profiles_data.csv",
        "/public/data.csv"
      ];
      
      for (const source of dataSources) {
        try {
          response = await fetch(source, { signal: abortController.signal });
          if (response.ok) {
            console.log(`Successfully loaded data from ${source}`);
            break;
          }
        } catch (e) {
          console.log(`Failed to load from ${source}: ${e.message}`);
        }
      }
      
      if (!response || !response.ok) {
        throw new Error("Could not load data from any source");
      }
      
      const csvText = await response.text();
      setLastUpdated(new Date());

      Papa.parse(csvText, {
        header: true,
        skipEmptyLines: true,
        fastMode: true,
        complete: function (results) {
          const processedData = results.data.map((row) => ({
            name: row["name"] || "Unknown",
            arcade: parseInt(row["game_badges"]) || 0,
            specialArcade: parseInt(row["special_game_badges"]) || 0,
            trivia: parseInt(row["trivia_badges"]) || 0,
            skill: parseInt(row["skill_badges"]) || 0,
            labs: parseInt(row["lab_badges"]) || 0,
            score: parseInt(row["total_points"]) || 0,
            milestone: row["milestone"] || "None",
          }));

          const validData = processedData.filter(p => !isNaN(p.score));
          setParticipants(validData);
          setIsLoading(false);
        },
        error: (error) => {
          console.error("Error parsing CSV:", error);
          setIsLoading(false);
        }
      });
    } catch (error) {
      if (!abortController.signal.aborted) {
        console.error("Failed to load data:", error);
        setIsLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    const abortController = new AbortController();
    
    // Load data immediately
    loadData(abortController);
    
    // Set up interval to refresh data every 5 minutes
    const intervalId = setInterval(() => {
      loadData(new AbortController());
    }, 5 * 60 * 1000); // 5 minutes in milliseconds
    
    return () => {
      abortController.abort();
      clearInterval(intervalId);
    };
  }, [loadData]);

  const handleSelectParticipant = useCallback((participant, index) => {
    setSelectedParticipant({ ...participant, rank: index });
  }, []);

  const getTrophyEmoji = useCallback((index) => {
    if (index === 0) return "🥇";
    if (index === 1) return "🥈";
    if (index === 2) return "🥉";
    if (index < 10) return "⭐";
    return "";
  }, []);

  const truncateName = useCallback((name, maxLength = 16) => {
    if (!name) return "Unknown";
    return name.length > maxLength ? name.substring(0, maxLength) + "..." : name;
  }, []);

  const ConfettiEffect = ({ isTop3 }) => {
    const confettiProps = useMemo(() => ({
      width: windowDimensions.width,
      height: windowDimensions.height,
      numberOfPieces: isTop3 ? 250 : 150,
      recycle: false,
      run: true,
      tweenDuration: 12000,
      gravity: 0.15,
      initialVelocityX: { min: -3, max: 3 },
      initialVelocityY: { min: -5, max: 2 },
      dragFriction: 0.05,
      colors: isTop3 ? 
        ['#FFD700', '#FFA500', '#FF4500', '#1a73e8', '#34A853', '#FBBC05'] : 
        ['#1a73e8', '#4285f4', '#34A853', '#FBBC05', '#EA4335'],
      opacity: isTop3 ? 0.9 : 0.8,
      confettiSource: {
        x: windowDimensions.width / 2,
        y: 0,
        w: windowDimensions.width,
        h: 0
      }
    }), [windowDimensions.width, windowDimensions.height, isTop3]);

    return <ReactConfetti {...confettiProps} />;
  };

  const renderDetailsModal = () => {
    if (!selectedParticipant) return null;
    const isTop3 = selectedParticipant.rank < 3;
    const isTop10 = selectedParticipant.rank < 10;
    const modalClass = isTop10 ? "modal-content top-modal" : "modal-content";
    const headerClass = isTop10 ? "modal-header top-header" : "modal-header";
    const rankTrophy = getTrophyEmoji(selectedParticipant.rank);

    return (
      <div className="modal-overlay">
        {isTop10 && <ConfettiEffect isTop3={isTop3} />}
        <div className={modalClass}>
          <div className={headerClass}>
            <h3>{rankTrophy} {selectedParticipant.name}</h3>
            <button 
              className="modal-close"
              onClick={() => setSelectedParticipant(null)}
            >
              ×
            </button>
          </div>
          <div className="modal-body">
            <div className="detail-row"><span>Arcade Badges:</span><span>{selectedParticipant.arcade}</span></div>
            <div className="detail-row"><span>Special Arcade Badges:</span><span>{selectedParticipant.specialArcade}</span></div>
            <div className="detail-row"><span>Trivia Badges:</span><span>{selectedParticipant.trivia}</span></div>
            <div className="detail-row"><span>Skill Badges:</span><span>{selectedParticipant.skill}</span></div>
            <div className="detail-row"><span>Lab-free Courses:</span><span>{selectedParticipant.labs}</span></div>
            <div className="detail-row highlight"><span>Total Points:</span><span>{selectedParticipant.score}</span></div>
            <div className="detail-row highlight"><span>Milestone:</span><span>{selectedParticipant.milestone}</span></div>
            {isTop10 && (
              <div className={isTop3 ? "top-badge elite-badge" : "top-badge"}>
                {isTop3 ? 
                  `🎉 Elite Top ${selectedParticipant.rank + 1} Performer 🎉` : 
                  `Top ${selectedParticipant.rank + 1} Performer`}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderTable = useMemo(() => (
    <div className="table-wrapper">
      <table className="mobile-table">
        <thead>
          <tr>
            <th style={{ backgroundColor: "#428548", color: "#fff" }}>Rank</th>
            <th style={{ backgroundColor: "#34A853", color: "#fff" }}>Name</th>
            <th style={{ backgroundColor: "#fbbc05", color: "#fff" }}>Points</th>
            <th style={{ backgroundColor: "#4285f4", color: "#fff" }}>Info</th>
          </tr>
        </thead>
        <tbody>
          {participants.map((p, index) => (
            <tr key={`mobile-${index}`}>
              <td>{index + 1}</td>
              <td className="name-cell">{getTrophyEmoji(index)}{truncateName(p.name)}</td>
              <td>{p.score}</td>
              <td>
                <button 
                  className="view-details-btn"
                  onClick={() => handleSelectParticipant(p, index)}
                >
                  View
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <table className="desktop-table">
        <thead>
          <tr>
            <th style={{ backgroundColor: "#428548", color: "#fff" }}>Rank</th>
            <th style={{ backgroundColor: "#34A853", color: "#fff" }}>Name</th>
            <th style={{ backgroundColor: "#fbbc05", color: "#fff" }}>Arcade</th>
            <th style={{ backgroundColor: "#ea4335", color: "#fff" }}>Special</th>
            <th style={{ backgroundColor: "#428548", color: "#fff" }}>Trivia</th>              
            <th style={{ backgroundColor: "#34A853", color: "#fff" }}>Skill</th>
            <th style={{ backgroundColor: "#fbbc05", color: "#fff" }}>Labs</th>
            <th style={{ backgroundColor: "#ea4335", color: "#fff" }}>Points</th>
            <th style={{ backgroundColor: "#4285f4", color: "#fff" }}>Milestone</th>
          </tr>
        </thead>
        <tbody>
          {participants.map((p, index) => (
            <tr key={`desktop-${index}`}>
              <td>{index + 1}</td>
              <td style={{ textAlign: "left" }}>{getTrophyEmoji(index)}{p.name}</td>
              <td>{p.arcade}</td>
              <td>{p.specialArcade}</td>
              <td>{p.trivia}</td>
              <td>{p.skill}</td>
              <td>{p.labs}</td>
              <td>{p.score}</td>
              <td>{p.milestone}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  ), [participants, getTrophyEmoji, truncateName, handleSelectParticipant]);

  return (
    <>
      <div className="container leaderboard-container">
        {isLoading ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading leaderboard data...</p>
          </div>
        ) : (
          <>
            {renderTable}
            {lastUpdated && (
              <div className="last-updated">
                <small>Last updated: {lastUpdated.toLocaleString()}</small>
                <small>Data refreshes every 10 minutes</small>
              </div>
            )}
          </>
        )}
      </div>
      {renderDetailsModal()}
    </>
  );
}
