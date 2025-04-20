import requests
from bs4 import BeautifulSoup
import json
import time
import pandas as pd
import argparse
import os


def scrape_cloud_profile(url):
    """
    Scrapes data from a Google Cloud Skills Boost public profile.

    Args:
        url (str): URL of the public profile

    Returns:
        dict: Profile data including badges categorized by type
    """
    # Send request to the profile page
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise exception for 4XX/5XX status codes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the profile: {e}")
        return None

    # Parse HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract profile data
    profile_data = {}

    # Profile name
    try:
        profile_name = soup.select_one('h1.ql-display-small').text.strip()
        profile_data['name'] = profile_name
    except (AttributeError, TypeError):
        profile_data['name'] = "Name not found"

    # Extract profile details
    try:
        profile_details = soup.select_one('div.public-profile__hero')
        if profile_details:
            # Extract completion stats
            stats = {}
            stat_elements = profile_details.select('div.ql-subhead-1')
            label_elements = profile_details.select('div.ql-headline-6')

            for i in range(min(len(stat_elements), len(label_elements))):
                label = label_elements[i].text.strip()
                value = stat_elements[i].text.strip()
                stats[label] = value

            profile_data['stats'] = stats
    except Exception as e:
        print(f"Error extracting profile details: {e}")
        profile_data['stats'] = {}

    # Initialize badge counters and lists
    badge_counts = {
        'lab_badges': 0,
        'skill_badges': 0,
        'game_badges': 0,
        'trivia_badges': 0,
        'special_game_badges': 0,  # Add this line
        'total_badges': 0
    }

    badges_by_type = {
        'lab_badges': [],
        'skill_badges': [],
        'game_badges': [],
        'trivia_badges': [],
        'special_game_badges': []  # Add this line
    }

    # Extract badges
    try:
        # Find all badge elements
        badge_containers = soup.select('div.profile-badge')

        if not badge_containers:
            print("No badge containers found with selector 'div.profile-badge'")
            return profile_data

        print(f"Found {len(badge_containers)} badge containers")

        # Process each badge
        for badge_container in badge_containers:
            badge_info = {}

            # Extract badge name - looking for the span with class ql-title-medium
            name_elem = badge_container.select_one('span.ql-title-medium')
            if not name_elem:
                # Try alternative selectors
                name_elem = badge_container.select_one('div.ql-title')
                if not name_elem:
                    continue

            badge_name = name_elem.text.strip()
            badge_info['name'] = badge_name

            # Badge date
            date_elem = badge_container.select_one('div.ql-caption')
            if date_elem:
                badge_info['date'] = date_elem.text.strip()

            # Badge image
            img_elem = badge_container.select_one('img')
            if img_elem and img_elem.has_attr('src'):
                badge_info['image'] = img_elem['src']

            # Identify badge type based on name rules
            badge_type = identify_badge_type(badge_name, badge_info.get('date', ''))
            badge_info['type'] = badge_type

            # Add badge to appropriate list and increment counter
            badges_by_type[badge_type].append(badge_info)
            badge_counts[badge_type] += 1
            badge_counts['total_badges'] += 1

        # Add badge counts and categorized badges to profile data
        profile_data['badge_counts'] = badge_counts
        profile_data['badges_by_type'] = badges_by_type
        profile_data['badges'] = sum(badges_by_type.values(), [])  # All badges in a flat list

    except Exception as e:
        print(f"Error extracting badges: {e}")
        import traceback
        traceback.print_exc()
        profile_data['badge_counts'] = badge_counts
        profile_data['badges_by_type'] = badges_by_type
        profile_data['badges'] = []

    return profile_data


def identify_badge_type(badge_name, badge_date):
    """
    Determines badge type based on name and date according to specified rules.

    Args:
        badge_name (str): Name of the badge
        badge_date (str): Date of the badge (if available)

    Returns:
        str: Badge type ('lab_badges', 'skill_badges', 'game_badges', or 'trivia_badges')
    """
    # Check for trivia badges based on date pattern
    if badge_name[-6:-2] == "Week":
        return 'trivia_badges'

    # Check for game badges
    if badge_name.startswith('Level ') or 'Base Camp' in badge_name:
        return 'game_badges'

    # Check for special game badge
    if badge_name == 'Arcade TechCare':
        return 'special_game_badges'

    # Check for lab badges (based on the list you provided earlier)
    lab_free_course_names = [
        "Digital Transformation with Google Cloud",
        "Exploring Data Transformation with Google Cloud",
        "Infrastructure and Application Modernization with Google Cloud",
        "Scaling with Google Cloud Operations",
        "Innovating with Google Cloud Artificial Intelligence",
        "Trust and Security with Google Cloud",
        "Google Drive",
        "Google Docs",
        "Google Slides",
        "Google Meet",
        "Google Sheets",
        "Google Calendar",
        "Responsible AI: Applying AI Principles with Google Cloud",
        "Responsible AI for Digital Leaders with Google Cloud",
        "Customer Experience with Google AI Architecture",
        "Machine Learning Operations (MLOps) with Vertex AI: Model Evaluation",
        "Conversational AI on Vertex AI and Dialogflow CX",
        "Building Complex End to End Self-Service Experiences in Dialogflow CX",
    ]

    if badge_name in lab_free_course_names:
        return 'lab_badges'

    # Default to skill badge if no other category matches
    return 'skill_badges'


def save_to_json(data, filename="profile_data.json"):
    """
    Saves the scraped data to a JSON file.

    Args:
        data (dict): The profile data to save
        filename (str): The name of the file to save to
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving data to file: {e}")


def print_badge_details(profile_url):
    """
    Print detailed information about all badges for analysis.

    Args:
        profile_url (str): URL of the profile to analyze
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    try:
        response = requests.get(profile_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        print("Listing badge details...")

        # Find all badge containers
        badge_containers = soup.select('div.profile-badge')

        if not badge_containers:
            print("No badge containers found with selector 'div.profile-badge'")
            return

        print(f"Found {len(badge_containers)} badge containers")

        for i, container in enumerate(badge_containers, 1):
            print(f"\nBadge {i}:")

            # Badge name
            name_elem = container.select_one('span.ql-title-medium')
            if name_elem:
                print(f"Name (ql-title-medium): {name_elem.text.strip()}")
            else:
                name_elem = container.select_one('div.ql-title')
                if name_elem:
                    print(f"Name (ql-title): {name_elem.text.strip()}")
                else:
                    print("Name: Not found")

            # Badge date
            date_elem = container.select_one('div.ql-caption')
            if date_elem:
                print(f"Date: {date_elem.text.strip()}")
            else:
                print("Date: Not found")

            # Badge classes - useful for debugging selectors
            print(f"Container classes: {container.get('class', [])}")

            # Print raw HTML for analysis
            # print(f"HTML: {container.prettify()[:300]}...")

    except Exception as e:
        print(f"Error listing badge details: {e}")

def calculate_points(badge_counts):
    """
    Calculates points based on badge counts.

    Args:
        badge_counts (dict): Dictionary containing counts of each badge type.

    Returns:
        int: Total points calculated.
    """
    game_badges_points = badge_counts.get('game_badges', 0) * 1
    trivia_badges_points = badge_counts.get('trivia_badges', 0) * 1
    skill_badges_points = (badge_counts.get('skill_badges', 0) // 2) * 1
    special_game_badges_points = badge_counts.get('special_game_badges', 0) * 2

    arcade_points = (
        game_badges_points +
        trivia_badges_points +
        skill_badges_points +
        special_game_badges_points
    )
    return arcade_points


def calculate_milestone(badge_counts):
    """
    Determines the milestone achieved and calculates points.

    Args:
        badge_counts (dict): Dictionary containing counts of each badge type.

    Returns:
        dict: Milestone details including milestone name, arcade points, bonus points, and total points.
    """
    milestones = [
        {
            "name": "Milestone 1",
            "requirements": {
                "game_badges": 4,
                "trivia_badges": 4,
                "skill_badges": 10,
                "lab_badges": 4
            },
            "points": {
                "game_badges": 4,
                "trivia_badges": 4,
                "skill_badges": 5,
                "bonus": 2
            }
        },
        {
            "name": "Milestone 2",
            "requirements": {
                "game_badges": 6,
                "trivia_badges": 6,
                "skill_badges": 20,
                "lab_badges": 8
            },
            "points": {
                "game_badges": 6,
                "trivia_badges": 6,
                "skill_badges": 10,
                "bonus": 8
            }
        },
        {
            "name": "Milestone 3",
            "requirements": {
                "game_badges": 8,
                "trivia_badges": 7,
                "skill_badges": 30,
                "lab_badges": 12
            },
            "points": {
                "game_badges": 8,
                "trivia_badges": 7,
                "skill_badges": 15,
                "bonus": 15
            }
        },
        {
            "name": "Ultimate Milestone",
            "requirements": {
                "game_badges": 10,
                "trivia_badges": 8,
                "skill_badges": 44,
                "lab_badges": 16
            },
            "points": {
                "game_badges": 10,
                "trivia_badges": 8,
                "skill_badges": 22,
                "bonus": 25
            }
        }
    ]

    # Check for milestone completion
    for milestone in reversed(milestones):  # Start from the highest milestone
        req = milestone["requirements"]
        if (badge_counts.get('game_badges', 0) >= req["game_badges"] and
                badge_counts.get('trivia_badges', 0) >= req["trivia_badges"] and
                badge_counts.get('skill_badges', 0) >= req["skill_badges"] and
                badge_counts.get('lab_badges', 0) >= req["lab_badges"]):
            # Calculate points
            points = milestone["points"]
            arcade_points = points["game_badges"] + points["trivia_badges"]
            special_game_bonus = min(badge_counts.get('special_game_badges', 0), 2)  # Max 2 special games
            arcade_points += special_game_bonus  # Add special game bonus points
            total_points = arcade_points + points["skill_badges"] + points["bonus"]

            # Add bonus points to total_points if milestone is met
            total_points += points["bonus"]

            return {
                "milestone": milestone["name"],
                "arcade_points": arcade_points,
                "bonus_points": points["bonus"],
                "total_points": total_points
            }

    # If no milestone is achieved
    return {
        "milestone": "No Milestone Achieved",
        "arcade_points": 0,
        "bonus_points": 0,
        "total_points": 0
    }

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Scrape Google Cloud Skills Boost profiles")
    parser.add_argument("--output", dest="output_file", default="profiles_data.csv",
                      help="Output CSV file path (default: profiles_data.csv)")
    args = parser.parse_args()
    
    try:
        # List of profile URLs
        profile_urls = [
            "https://www.cloudskillsboost.google/public_profiles/ddfc7723-216a-444c-ab34-cba5d7807296",
            "https://www.cloudskillsboost.google/public_profiles/104ba705-a4ed-422e-9599-e8cbcdfb0be6",
            # Add more URLs as needed - make sure these are valid profile URLs
        ]

        # List to store profile data
        profiles_data = []

        print("Scraping profiles...")
        start_time = time.time()

        for url in profile_urls:
            print(f"Scraping profile: {url}")
            profile_data = scrape_cloud_profile(url)

            if profile_data:
                # Add the profile data to the list
                profiles_data.append({
                    "name": profile_data.get("name", "N/A"),
                    "game_badges": profile_data.get("badge_counts", {}).get("game_badges", 0),
                    "special_game_badges": profile_data.get("badge_counts", {}).get("special_game_badges", 0),
                    "trivia_badges": profile_data.get("badge_counts", {}).get("trivia_badges", 0),
                    "skill_badges": profile_data.get("badge_counts", {}).get("skill_badges", 0),
                    "lab_badges": profile_data.get("badge_counts", {}).get("lab_badges", 0),
                    "arcade_points": calculate_points(profile_data.get("badge_counts", {})),
                    "milestone": calculate_milestone(profile_data.get("badge_counts", {})).get("milestone", "No Milestone"),
                    "bonus_points": calculate_milestone(profile_data.get("badge_counts", {})).get("bonus_points", 0),
                    "total_points": (calculate_points(profile_data.get("badge_counts", {})) + 
                                    calculate_milestone(profile_data.get("badge_counts", {})).get("bonus_points", 0))
                })

        print(f"Scraping completed in {time.time() - start_time:.2f} seconds")

        # Create a DataFrame with the required columns
        columns = [
            'name', 'game_badges', 'special_game_badges', 'trivia_badges',
            'skill_badges', 'lab_badges', 'arcade_points', 'milestone',
            'bonus_points', 'total_points'
        ]
        
        if profiles_data:
            # Create DataFrame from existing data
            df = pd.DataFrame(profiles_data)
            # Sort by total points if data exists
            df.sort_values(by=['total_points'], ascending=False, inplace=True)
        else:
            # Create empty DataFrame with specified columns
            print("No profiles were scraped. Creating empty DataFrame with required columns.")
            df = pd.DataFrame(columns=columns)

        # Save the DataFrame to a CSV file
        output_file = args.output_file
        
        # Create parent directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        df.to_csv(output_file, index=False)
        print(f"Data saved to {output_file}")
        
    except Exception as e:
        print(f"An error occurred in the scraper: {e}")
        import traceback
        traceback.print_exc()
        
        # Create an empty DataFrame with the required columns as a fallback
        columns = [
            'name', 'game_badges', 'special_game_badges', 'trivia_badges',
            'skill_badges', 'lab_badges', 'arcade_points', 'milestone',
            'bonus_points', 'total_points'
        ]
        df = pd.DataFrame(columns=columns)
        
        # Save the empty DataFrame to the output file
        output_file = args.output_file
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        df.to_csv(output_file, index=False)
        print(f"Created empty data file at {output_file} due to error")
