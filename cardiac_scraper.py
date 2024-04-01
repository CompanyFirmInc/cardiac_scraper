import re
import csv
import praw
import configparser
import pandas as pd
import concurrent.futures
from ftfy import fix_text
from datetime import datetime
from combine_module import combine
from multiprocessing import Pool, Lock


def format_date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')  # Format the date


def setup():
    """Loads data from an ini file for setting up the scraper

    Returns:
        dict: A dict with the data from the ini file
    """
    try:
        config = configparser.ConfigParser()
        config.read('./cardiac_scraper.ini')
        temp_conf = config['scraper']
        ini_data = {
            'id': temp_conf['client_id'],
            'secret': temp_conf['client_secret'],
            'user_agent': temp_conf['user_agent'],
            'timeout': config['DEFAULT']['timeout']}
        
    except KeyError as e:
        exit(f"Invalid Ini File: {e} value(s) incorrect")
    
    return ini_data


def search_subreddit(reddit: tuple, subreddit: str, term: str) -> None:
    """A function which runs on each thread designed to collect posts and write them to a csv file.

    Args:
        reddit (object): The API object which is used to scrape the posts, this is passed between fns.
        subreddit (str): the name of the subreddit being scraped.
        term (str): The search terms we are using to filter results which will be scraped.
    """
    posts = {}
    
    unattr_posts = 0
    posts_collected = 0
    
    # Search the subreddit for the term and write post details to the CSV
    for submission in reddit.subreddit(subreddit).search(term, limit=10):
        posts_collected += 1
        posts.append([submission.title,submission.author.name if submission.author else f"Deleted {unattr_posts}",
                      submission.title,
                      format_date(submission.created_utc),
                      fix_text(submission.selftext)])
        
        print(f"Scraping post: {submission.title}", flush=True)

    # Open the result file
    with open(f"reddit_posts_{subreddit}.csv", 'w+', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(['Author', 'Title', 'Post Date', 'Text'])
        writer.writerows(posts)
    
    return


def process_search_terms(subreddit: str):
    """A function designed to be multiprocessed which handles calling multiple threads
    to parallelise the web scraping of reddit data from multiple subreddits.

    Args:
        subreddit (str): the subreddit to scrape
    """
    
    # Define the subreddit and search terms
    search_terms = ["cardiac contractility modulation" , "cardiac implantable electronic device" , 
                    "cardiac resynchronisation" , "cardiac resynchronization" , "CRT" , "ICD" , 
                    "implantable cardioverter defibrillator" , "implantable cardioverter-defibrillator" , "leadless pacemaker" , 
                    "Pacemaker" , "S-ICD" , "subcutaneous implantable cardioverter defibrillator" , "subcutaneous implantable cardioverter-defibrillator"]
    
    # need api access per process so it isn't being passed around
    reddit = praw.Reddit(client_id='x',
                        client_secret='x',
                        user_agent='x',
                        ratelimit_seconds=300)
    
    # multiprocess searching
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as exec:
        for term in search_terms:
            exec.submit(search_subreddit,(Lock(), reddit),subreddit,term)
    
    print(f"Data written to reddit_posts_{subreddit}.csv", flush=True)
    

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


def main(config):
    # Initialize PRAW with your client credentials
    subreddits = ['AskDocs', 'Heartfailure', 'askCardiology', 'pacemakerICD']
    
    # create a process pool with a list of subreddits
    with Pool(4) as processes:
        processes.map(process_search_terms, subreddits, config)

    try:
        for sub in subreddits: cleanup(sub)
    except FileNotFoundError as e:
        exit(e)


if __name__ == "__main__":
    config = setup()
    main(config)
    combine()
