import configparser


def setup():
    """Loads data from an ini file for setting up the scraper

    Returns:
        dict: A dict with the data from the ini file
    """
    try:
        config = configparser.ConfigParser()
        config.read('./praw.ini')
        temp_conf = config['scraper']
        ini_data = {
            'id': temp_conf['client_id'],
            'secret': temp_conf['client_secret'],
            'user_agent': temp_conf['user_agent'],
            'timeout': config['DEFAULT']['timeout']}
        
    except KeyError as e:
        exit(f"Invalid Ini File: {e} value(s) incorrect")
    
    return ini_data