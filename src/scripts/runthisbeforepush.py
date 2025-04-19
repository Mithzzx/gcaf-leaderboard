import pandas as pd
import os

# Get the path to the project root (two levels up from the script location)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
output_path = os.path.join(project_root, 'public', 'data.csv')

df = pd.read_csv(r"D:\gcaf reports\18thApr.csv")

columns_to_keep = [
    "User Name",
    "# of Arcade Games Completed",
    "# of Trivia Games Completed",
    "# of Skill Badges Completed",
    "# of Lab-free Courses Completed",
]

df_cleaned = df[columns_to_keep]

df_cleaned.to_csv(output_path, index=False)

print(f"Cleaned CSV saved as '{output_path}'")
