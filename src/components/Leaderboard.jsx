import React, { useEffect, useState } from "react";
import Papa from "papaparse";

export default function Leaderboard() {
  const [participants, setParticipants] = useState([]);

  useEffect(() => {
    Papa.parse("/data.csv", {
      download: true,
      header: true,
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
            name: row["Name"] || "Unknown",
            score,
            milestone,
            profile: row["Google Cloud Skills Boost Profile URL"],
          };
        });

        const sorted = withScores
          .filter((p) => !isNaN(p.score))
          .sort((a, b) => b.score - a.score);

        setParticipants(sorted);
      },
    });
  }, []);

  return (
    <div className="container">
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Name</th>
              <th>Points</th>
              <th>Milestone</th>
            </tr>
          </thead>
          <tbody>
            {participants.map((p, index) => (
              <tr key={index}>
                <td>{index + 1}</td>
                <td>{p.name}</td>
                <td>{p.score}</td>
                <td>{p.milestone}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
