import pandas as pd

df = pd.read_csv("public/rawData.csv")

columns_to_keep = [
    "User Name",
    "# of Arcade Games Completed",
    "# of Trivia Games Completed",
    "# of Skill Badges Completed",
    "# of Lab-free Courses Completed",
]

df_cleaned = df[columns_to_keep]

df_cleaned.to_csv("public/data.csv", index=False)

print("Cleaned CSV saved as 'data.csv'")
