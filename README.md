# GCAF Leaderboard

A leaderboard application to track and display Google Cloud Arcade Festival participant progress.

## Project Structure

```
gcaf-leaderboard/
├── backend/                 # Backend code
│   ├── logs/                # Log files
│   ├── requirements.txt     # Python dependencies
│   └── src/                 # Backend source code
│       ├── cloud_profile_scraper.py  # Script to scrape cloud profiles
│       ├── scheduler.py     # Script to run scraper
│       └── runthisbeforepush.py  # Pre-deployment script
├── data/                    # Data storage
│   ├── backup/              # Backup data files
│   └── profiles/            # Profile data
│       └── profiles_data.csv # Generated data file used by frontend
├── public/                  # Static files
│   └── data.csv             # Backup static data file
├── src/                     # Frontend source code
│   ├── components/          # React components
│   │   └── Leaderboard.jsx  # Main leaderboard display component
│   ├── App.jsx              # Main React application
│   ├── App.css              # Application styles
│   ├── main.jsx             # React entry point
│   └── index.css            # Global styles
├── profiles_data.csv        # Generated data file (root level for compatibility)
├── start_scraper.sh         # Script to start the data collection
└── stop_scraper.sh          # Script to stop the data collection
```

## Data Flow

1. **Data Collection**: 
   - `cloud_profile_scraper.py` scrapes participant profiles from Google Cloud Skills Boost
   - Extracts game badges, special game badges, trivia badges, skill badges, and lab badges
   - Calculates points and milestone achievements

2. **Data Storage**:
   - Scraped data is saved to multiple locations:
     - `/data/profiles/profiles_data.csv` (primary location)
     - `/profiles_data.csv` (root, for backwards compatibility)
     - `/public/data.csv` (for direct serving)

3. **Data Display**:
   - `Leaderboard.jsx` reads the data from any of the above locations
   - Displays participant rankings, scores, and achievements in a clean UI
   - Updates automatically when the CSV file changes

## How to Run

### Frontend (React)

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### Backend (Python Scraper)

```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Run the scraper
./start_scraper.sh
```

## Implementation Details

- The frontend is built with React and Vite
- The scraper is built with Python using BeautifulSoup for HTML parsing
- The data is stored in CSV format for easy processing

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
  </tr>
</table>
