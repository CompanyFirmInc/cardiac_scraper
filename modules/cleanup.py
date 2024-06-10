import re
import csv
import pandas as pd


def cleanup(subreddit: str):
    df = pd.read_csv(f"reddit_posts_{subreddit}.csv")
    total_posts = len(df)

    df.drop_duplicates(subset=df.columns[1], keep='first', inplace=True)
    minus_duplicate_count = len(df)
    duplicates_removed = total_posts - minus_duplicate_count
    df.to_csv(f'reddit_posts_{subreddit}_deduplicated.csv', index=False)

    print(f"posts collected from inital scrape: {total_posts}")
    print(f"Duplicate rows removed: {duplicates_removed}")
    print(f"Saved to reddit_posts_{subreddit}_deduplicated.csv")

    distinction = ["step", "grand", "girl", "boy"]
    relations = [
        "auntie", "caregiver", "fiance", "fiancé", "fiancee", "fiancée", "gramps", "husband", "neighbour",
        "nephew", "niece", "other half", "papa", "sibling", "spouse", "uncle", "wife", "friend", "mom", "ma", 
        "mama", "mother", "brother", "son", "sister", "daughter", "cousin", "child", "carer", "aunt", "bro", 
        "sis", "partner", "mum", "gran", "father", "dad"]

    pattern = re.compile(r"\b(" + "|".join(distinction) + r")?(-|\s)?(" + "|".join(relations) + r')((-|\s*)in(-|\s*)law?)?')
    df = pd.read_csv(f'reddit_posts_{subreddit}_deduplicated.csv')
    total_posts = len(df)
    filtered_df = df[df.iloc[:, 1].str.lower().str.contains(pattern, regex=True, na=False) |
                    df.iloc[:, 3].str.lower().str.contains(pattern, regex=True, na=False)]

    filtered_posts = len(filtered_df)
    filtered_delta = total_posts - filtered_posts
    filtered_df.to_csv(f'filtered_reddit_posts_{subreddit}.csv', index=False)

    print(f"Count of Total Posts: {total_posts}")
    print(f"Number of posts removed: {filtered_delta}")

    df = pd.read_csv(f'filtered_reddit_posts_{subreddit}.csv')
    df['Source'] = subreddit
    df.to_csv(f'finished_reddit_data_{subreddit}.csv', index=False)

    with open(f'{subreddit}_stats.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Posts collected', 'duplicates removed', 'count filtered - finished total'])
        writer.writerow([total_posts, duplicates_removed, filtered_delta])
            
    print(f"Count of filtered posts: {filtered_delta}")