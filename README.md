# GCAF Leaderboard

## Overview
This project displays a leaderboard for the Google Cloud Arcade Festival (GCAF), tracking participants' progress across various activities.

## Features
- Visual representation of participant achievements
- Tracking of arcade games, trivia games, skill badges, and lab-free courses
- Responsive design for all devices

## Setup Instructions
1. Clone the repository
```bash
git clone <repository-url>
cd gcaf-leaderboard
```

2. Install dependencies
```bash
npm install
# or
yarn install
```

3. Process the data
```bash
cd src/scripts
python runthisbeforepush.py
```

4. Start the development server
```bash
npm run dev
# or
yarn dev
```

## Data Processing
The system processes CSV reports from GCAF to generate the leaderboard data. The script in `src/scripts/runthisbeforepush.py` cleans and formats the data for display.

## 👥 Contributors

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/kabillanta" target="_blank">
        <img src="https://github.com/kabillanta.png" width="100" alt="kabillanta's profile picture"/><br/>
        <sub><b>Kabillan TA</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/pr1ncegupta" target="_blank">
        <img src="https://github.com/pr1ncegupta.png" width="100" alt="pr1ncegupta's profile picture"/><br/>
        <sub><b>Prince Gupta</b></sub>
      </a>
    </td>
    <!-- Add more contributors below -->
  </tr>
</table>

<!-- To add yourself as a contributor:
1. Fork the repository
2. Add your profile in the table above
3. Submit a pull request
-->


