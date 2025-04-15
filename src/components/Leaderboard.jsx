import React, { useEffect, useState, useMemo, useCallback, Suspense } from "react";
import Papa from "papaparse";
import ReactConfetti from "react-confetti";

export default function Leaderboard() {
  const [participants, setParticipants] = useState([]);
  const [selectedParticipant, setSelectedParticipant] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [windowDimensions, setWindowDimensions] = useState({
    width: window.innerWidth,
    height: window.innerHeight
  });
  
  // Track window dimensions for confetti - optimized with debounce
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
  
  // Load data with optimized parsing configuration
  useEffect(() => {
    const abortController = new AbortController();
    
    const loadData = async () => {
      setIsLoading(true);
      try {
        // Use fetch API directly for better control over the loading process
        const response = await fetch("/data.csv", { signal: abortController.signal });
        const csvText = await response.text();
        
        Papa.parse(csvText, {
          header: true,
          skipEmptyLines: true,
          fastMode: true, // Use fast mode for numeric data
          complete: function (results) {
            const withScores = results.data.map((row) => {
              const arcade = parseInt(row["# of Arcade Games Completed"]) || 0;
              const trivia = parseInt(row["# of Trivia Games Completed"]) || 0;
              const skill = parseInt(row["# of Skill Badges Completed"]) || 0;
              const labs = parseInt(row["# of Lab-free Courses Completed"]) || 0;
              
              let score = arcade + trivia + Math.floor(skill / 2);
              let milestone = "None";
              
              if (arcade >= 10 && trivia >= 8 && skill >= 44 && labs >= 16) {
                score += 25;
                milestone = "M4";
              } else if (arcade >= 8 && trivia >= 7 && skill >= 30 && labs >= 12) {
                score += 15;
                milestone = "M3";
              } else if (arcade >= 6 && trivia >= 6 && skill >= 20 && labs >= 8) {
                score += 8;
                milestone = "M2";
              } else if (arcade >= 4 && trivia >= 4 && skill >= 10 && labs >= 4) {
                score += 2;
                milestone = "M1";
              }
              
              return {
                name: row["User Name"] || "Unknown",
                arcade,
                trivia,
                skill,
                labs,
                score,
                milestone,
                profile: row["Google Cloud Skills Boost Profile URL"],
              };
            });
            
            const sorted = withScores
              .filter((p) => !isNaN(p.score))
              .sort((a, b) => b.score - a.score);
            
            setParticipants(sorted);
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
    };
    
    loadData();
    
    return () => {
      abortController.abort();
    };
  }, []);
  
  // Close the modal when clicking outside - memoized handler for better performance
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (selectedParticipant && !event.target.closest('.modal-content') && !event.target.closest('.view-details-btn')) {
        setSelectedParticipant(null);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [selectedParticipant]);

  // Function to handle selecting a participant for detail view
  const handleSelectParticipant = useCallback((participant, index) => {
    setSelectedParticipant({...participant, rank: index});
  }, []);

  // Helper function to get trophy emoji based on rank
  const getTrophyEmoji = useCallback((index) => {
    if (index === 0) return "🥇"; // Gold medal for 1st
    if (index === 1) return "🥈"; // Silver medal for 2nd
    if (index === 2) return "🥉"; // Bronze medal for 3rd
    if (index < 10) return "⭐"; // Trophy for top 10
    return "";
  }, []);

  // Helper function to truncate names if they are too long
  const truncateName = useCallback((name, maxLength = 16) => {
    if (!name) return "Unknown";
    return name.length > maxLength ? name.substring(0, maxLength) + "..." : name;
  }, []);

  // Enhanced confetti component with better performance and visual effects
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

  // Render the details modal
  const renderDetailsModal = () => {
    if (!selectedParticipant) return null;
    
    // Determine if the participant is in top 10 or top 3
    const isTop3 = selectedParticipant.rank < 3;
    const isTop10 = selectedParticipant.rank < 10;
    const modalClass = isTop10 ? "modal-content top-modal" : "modal-content";
    const headerClass = isTop10 ? "modal-header top-header" : "modal-header";
    
    // Get the appropriate trophy emoji for the header
    const rankTrophy = getTrophyEmoji(selectedParticipant.rank);
    
    return (
      <div className="modal-overlay">
        {/* Enhanced Confetti for top performers */}
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
            <div className="detail-row">
              <span>Arcade Games:</span>
              <span>{selectedParticipant.arcade || 0}</span>
            </div>
            <div className="detail-row">
              <span>Trivia Games:</span>
              <span>{selectedParticipant.trivia || 0}</span>
            </div>
            <div className="detail-row">
              <span>Skill Badges:</span>
              <span>{selectedParticipant.skill || 0}</span>
            </div>
            <div className="detail-row">
              <span>Lab-free Courses:</span>
              <span>{selectedParticipant.labs || 0}</span>
            </div>
            <div className="detail-row highlight">
              <span>Total Points:</span>
              <span>{selectedParticipant.score || 0}</span>
            </div>
            <div className="detail-row highlight">
              <span>Milestone:</span>
              <span>{selectedParticipant.milestone || "None"}</span>
            </div>
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

  // Memoize the table rendering for better performance
  const renderTable = useMemo(() => (
    <div className="table-wrapper">
      {/* Mobile view table (only visible on small screens) */}
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
      
      {/* Desktop view table (only visible on larger screens) */}
      <table className="desktop-table">
        <thead>
          <tr>
            <th style={{ backgroundColor: "#428548", color: "#fff" }}>Rank</th>
            <th style={{ backgroundColor: "#34A853", color: "#fff" }}>Name</th>
            <th style={{ backgroundColor: "#fbbc05", color: "#fff" }}>Arcade</th>
            <th style={{ backgroundColor: "#ea4335", color: "#fff" }}>Trivia</th>
            <th style={{ backgroundColor: "#428548", color: "#fff" }}>Skill</th>              
            <th style={{ backgroundColor: "#34A853", color: "#fff" }}>Labs</th>
            <th style={{ backgroundColor: "#fbbc05", color: "#fff" }}>Points</th>
            <th style={{ backgroundColor: "#ea4335", color: "#fff" }}>Milestone</th>
          </tr>
        </thead>
        <tbody>
          {participants.map((p, index) => (
            <tr key={`desktop-${index}`}>
              <td>{index + 1}</td>
              <td style={{textAlign: "left"}}>{getTrophyEmoji(index)}{p.name}</td>
              <td>{p.arcade}</td>
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
          renderTable
        )}
      </div>
      
      {renderDetailsModal()}
    </>
  );
}
