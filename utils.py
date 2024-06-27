from datetime import datetime

def convert_to_locale(timestamp):
    """
    Convert timestamp to locale YY-MM-DD hh:mm:ss format.
    """
    if timestamp == 'N/A':
        return timestamp
    dt = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S%z')
    return dt.strftime('%Y-%m-%d %H:%M:%S')