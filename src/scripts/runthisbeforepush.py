import pandas as pd

# Using proper path with forward slashes to avoid escape sequence issues
df = pd.read_csv("public/rawData.csv")

columns_to_keep = [
    "User Name",
    "# of Arcade Games Completed",
    "# of Trivia Games Completed",
    "# of Skill Badges Completed",
    "# of Lab-free Courses Completed",
]

df_cleaned = df[columns_to_keep]

df_cleaned.to_csv("public/dataApril10.csv", index=False)

print("Cleaned CSV saved as 'data.csv'")
