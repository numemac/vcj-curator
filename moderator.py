import datetime
import os
import math
import praw

VERSION = '0.1'
AUTHOR = 'Numerous-Macaroon224'
SUBREDDIT_NAME = 'vegancirclejerk'
USER_AGENT = f'python:vcj_mod_bot:v{VERSION} (by /u/{AUTHOR})'

# Found by inspecting the network at
# https://www.reddit.com/r/vegancirclejerk/about/removal
# and looking for the GET request to
# https://oauth.reddit.com/api/v1/vegancirclejerk/removal_reasons.json
REMOVAL_REASON_NOT_FUNNY = 'cdb7617c-6b0e-4543-85ed-8fc5cf2b8c94'
REMOVAL_MESSAGE_NOT_FUNNY = '''Your submission did not reach a competitive time-based upvote target.
To ensure maximal dank-ness, our bot is removing it to give other posts more attention.
This is activism, right?'''

# Create a Reddit instance
reddit = praw.Reddit(
    client_id=os.environ.get('REDDIT_CLIENT_ID'),
    client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
    user_agent=USER_AGENT,
    username=os.environ.get('REDDIT_USERNAME'),
)

def hour_valuation(hour_of_day : int):
    """
    Calculates a value relative to Reddit's activity patterns for a given hour.

    Parameters:
    hour_of_day (int): The hour of the day in 24-hour format.

    Returns:
    float: The valuation of the hour. Returns 0.6 if the hour is between 
    7pm and 7am EST, and 1.67 otherwise.
    """
    # 7pm EST to 7am EST
    if hour_of_day < 12:
        return 1.0 * 0.6
    
    return 1.0 / 0.6
    

# returns: int
# exponential growth
def discussion_score(_num_comments : int):
    """
    Calculates the discussion score of a submission based on the number of comments.

    Parameters:
    _num_comments (int): The number of comments on the submission.

    Returns:
    int: The discussion score of the submission. The score is calculated by
         applying an exponential growth function to the number of comments.
    """
    return math.floor(_num_comments ** 1.5)

def minutes_ellapsed(created_utc : int):
    """
    Calculates the number of minutes that have elapsed since the creation of a submission.

    Parameters:
    created_utc (int): The Unix timestamp of the creation of the submission.

    Returns:
    int: The number of minutes that have elapsed since the creation of the submission.
    """
    now_utc = int(datetime.datetime.now(datetime.UTC).timestamp())
    return int((now_utc - created_utc) / 60)

def adjusted_minutes_ellapsed(created_utc : int, _minutes_ellapsed : int):
    """
    Calculates the adjusted number of minutes that have elapsed since the creation of a submission.
    Minutes are adjusted based on the time of day the submission was created.
    This is done to account for the varying levels of activity on Reddit at different times of the day.

    Parameters:
    created_utc (int): The Unix timestamp of the creation of the submission.

    Returns:
    int: The adjusted number of minutes that have elapsed since the creation of the submission.
    """
    minute_value_summation = 0
    for i in range(0, _minutes_ellapsed):
        unix_timestamp = created_utc + (i * 60)
        hour_of_day = datetime.datetime.fromtimestamp(unix_timestamp, datetime.UTC).hour
        minute_value_summation += hour_valuation(hour_of_day)
    return math.floor(minute_value_summation)

def calculate_target(_minutes_ellapsed : int = None, _submission : praw.models.Submission = None):
    """
    Calculates the target score for a submission based on the number of upvotes
        and the time it has been visible.

    Parameters:
    _minutes_ellapsed (int): The number of minutes that have elapsed since the
        creation of the submission.
    _submission (praw.models.Submission): The submission object.

    Returns:
    int: The target score for the submission.
    """

    # Get the minutes ellapsed from the submission if it is not provided
    if _minutes_ellapsed is None and _submission is None:
        raise ValueError("calculate_target requires either _minutes_ellapsed or _submission")
    elif _submission is not None:
        if _minutes_ellapsed is None:
            _minutes_ellapsed = adjusted_minutes_ellapsed(
                _submission.created_utc,
                minutes_ellapsed(_submission.created_utc)
            )

    # give every submission some time to get upvotes
    if _minutes_ellapsed < 30:
        return 1

    # after 12 hours, the target score will not increase
    _minutes_ellapsed = min(_minutes_ellapsed, 720)

    _hours_ellapsed = _minutes_ellapsed / 60

    # 1 upvote per 10 minutes
    # 30 minutes = 3 upvotes
    # 60 minutes = 6 upvotes
    # 120 minutes = 12 upvotes
    # 240 minutes = 24 upvotes
    # 360 minutes = 36 upvotes
    # 720 minutes = 72 upvotes
    base_target = math.floor(_minutes_ellapsed / 10)
    
    # Expect upvote rate to pick up after the first hour
    # 30 minutes = 1 + (0.5/12) = 1.0417
    # 60 minutes = 1 + (1/12) = 1.0833
    # 120 minutes = 1 + (2/12) = 1.1667
    # 240 minutes = 1 + (4/12) = 1.3333
    # 360 minutes = 1 + (6/12) = 1.5
    # 720 minutes = 1 + (12/12) = 2
    hour_multiplier = 1 + (_hours_ellapsed / 12)

    # 30 minutes = 3 * 1.0417 = 3.125
    # 60 minutes = 6 * 1.0833 = 6.5
    # 120 minutes = 12 * 1.1667 = 14
    # 240 minutes = 24 * 1.3333 = 32
    # 360 minutes = 36 * 1.5 = 54
    # 720 minutes = 72 * 2 = 144
    return math.floor(base_target * hour_multiplier)

def allow_submission(_submission : praw.models.Submission):
    """
    Allow a submission to stay on the subreddit.

    Parameters:
    _submission (praw.models.Submission): The submission object.

    Returns:
    None
    """
    return None

def remove_submission(_submission : praw.models.Submission):
    """
    Remove a submission from the subreddit.

    Parameters:
    _submission (praw.models.Submission): The submission object.

    Returns:
    None
    """
    _submission.mod.remove(
        reason_id=REMOVAL_REASON_NOT_FUNNY,
        mod_note=submission_str(_submission)
    )
    _submission.mod.send_removal_message(
        type='public_as_subreddit',
        message=REMOVAL_MESSAGE_NOT_FUNNY
    )
    return None

def should_remove(_submission : praw.models.Submission):
    """
    Determine if a submission should be removed from the subreddit.

    Parameters:
    _submission (praw.models.Submission): The submission object.

    Returns:
    bool: True if the submission should be removed, False otherwise.
    """
    _discussion_score = discussion_score(_submission.num_comments)
    _combined_score = _submission.score + _discussion_score
    return _combined_score < calculate_target(_submission=_submission)

def submission_action(_submission : praw.models.Submission):
    """
    Determine the action to take on a submission.

    Parameters:
    _submission (praw.models.Submission): The submission object.

    Returns:
    function: The function to call with the submission.
    """
    if should_remove(_submission=_submission):
        return remove_submission
    else:
        return allow_submission

def get_new_submissions(limit : int):
    """
    Get the newest submissions from the subreddit.
    
    Parameters:
    limit (int): The number of submissions to retrieve.

    Returns:
    praw.models.listing.generator.ListingGenerator: A generator that yields submission objects.
    """
    return reddit.subreddit(SUBREDDIT_NAME).new(limit=limit)

def submission_str(_submission : praw.models.Submission):
    """
    Create a string representation of a submission for logging purposes.

    Parameters:
    _submission (praw.models.Submission): The submission object.

    Returns:
    str: A string representation of the submission.
    """
    lines = []
    _minutes_ellapsed = minutes_ellapsed(_submission.created_utc)
    _adjusted_minutes_ellapsed = adjusted_minutes_ellapsed(
        _submission.created_utc,
        _minutes_ellapsed
    )
    _discussion_score = discussion_score(_submission.num_comments)
    _combined_score = _submission.score + _discussion_score
    _target_score = calculate_target(_adjusted_minutes_ellapsed)
    lines.append(f"title: {_submission.title}")
    lines.append(f"minutes_ellapsed: {_minutes_ellapsed}")
    lines.append(f"adjusted_minutes_ellapsed: {_adjusted_minutes_ellapsed}")
    lines.append(f"num_comments: {_submission.num_comments}")
    lines.append(f"score: {_submission.score}")
    lines.append(f"discussion_score: {_discussion_score}")
    lines.append(f"combined_score: {_combined_score}")
    lines.append(f"target score: {_target_score}")
    return "\n".join(lines)

def evaluate_submission(_submission : praw.models.Submission):
    """
    Evaluate a submission and take the appropriate action.

    Parameters:
    _submission (praw.models.Submission): The submission object.

    Returns:
    None
    """
    action = submission_action(_submission)
    action(_submission)

    print(submission_str(_submission))
    print("Action: ", action.__name__)
    return None

# loop through the submissions
for _submission in get_new_submissions(10):
    evaluate_submission(_submission)
    print("----")
