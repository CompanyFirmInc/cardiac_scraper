import re
import csv
import praw
import concurrent.futures
import multiprocessing as mp

from time import sleep
from ftfy import fix_text
from modules.helpers import touch, format_date
from modules.cleanup import cleanup
from modules.combine_module import combine



def search_subreddit(lock: mp.Lock, reddit, subreddit: str, term: str) -> None:
    """A function which runs on each thread designed to collect posts and write them to a csv file.

    Args:
        lock (mp.lock): A multiprocessing lock to prevent threads/processes opening the file simultaneously.
        reddit (object): The API object which is used to scrape the posts, this is passed between fns.
        subreddit (str): the name of the subreddit being scraped.
        term (str): The search terms we are using to filter results which will be scraped.
    """
    posts = {}
    unattr_posts = 0
    posts_collected = 0
    
    print(term)
    
    # Search the subreddit for the term and write post details to the CSV
    for submission in reddit.subreddit(subreddit).search(term, limit=1000):
        posts_collected += 1
        posts.append([submission.title,submission.author.name if submission.author else f"Deleted {unattr_posts}",
                    submission.title,
                    format_date(submission.created_utc),
                    fix_text(submission.selftext)])
        
        print(f"Scraping post: {submission.title}")

    # Open the result file
    filename = f"./reddit_posts_{subreddit}.csv"
    lock.acquire()
    try:
        with open(filename, 'w') as out_file:
            writer = csv.writer(out_file)
            # Write the header row
            writer.writerow(['Author', 'Title', 'Post Date', 'Text'])
            writer.writerows(posts)
    finally:
        lock.release()


def process_search_terms(subreddit: str):
    """A function designed to be multiprocessed which handles calling multiple threads
    to parallelise the web scraping of reddit data from multiple subreddits.

    Args:
        subreddit (str): the subreddit to scrape
    """
    
    # Define the subreddit and search terms
    search_terms = ["cardiac contractility modulation", "cardiac implantable electronic device", 
                    "cardiac resynchronisation", "cardiac resynchronization", "CRT", "ICD", 
                    "implantable cardioverter defibrillator", "implantable cardioverter-defibrillator", 
                    "leadless pacemaker", "Pacemaker", "S-ICD", "subcutaneous implantable cardioverter defibrillator", 
                    "subcutaneous implantable cardioverter-defibrillator"]
    
    # need api access per process so it isn't being passed around
    reddit = praw.Reddit("scraper", ratelimit_seconds=300)
    
    # multiprocess searching
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as exec:
        for term in search_terms:
            exec.submit(search_subreddit, mp.Lock(), reddit, subreddit, term)
            sleep(1)
    
    print(f"Data written to reddit_posts_{subreddit}.csv", flush=True)


def main():
    # Initialize PRAW with your client credentials
    subreddits = ['AskDocs', 'Heartfailure', 'askCardiology', 'pacemakerICD']
    
    for subreddit in subreddits:
        filename = f"reddit_posts_{subreddit}.csv"
        touch(filename)
    
    processes = []
    
    # create a process pool with a list of subreddits
    for sub in subreddits:
        process = mp.Process(target=process_search_terms, args=(sub,))
        processes.append(process)
        process.start()
    
    for process in processes:
        process.join()

    # try:
    #     for sub in subreddits: 
    #         cleanup(sub)
    # except FileNotFoundError as e:
    #     exit(e)


if __name__ == "__main__":
    main()
    # combine()
