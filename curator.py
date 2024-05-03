"""
curator.py
"""

import datetime
import math
import praw

SUBREDDIT_NAME="vegancirclejerk"

# Found by inspecting the network at
# https://www.reddit.com/r/vegancirclejerk/about/removal
# and looking for the GET request to
# https://oauth.reddit.com/api/v1/vegancirclejerk/removal_reasons.json
REMOVAL_REASON_NOT_FUNNY = 'cdb7617c-6b0e-4543-85ed-8fc5cf2b8c94'
REMOVAL_MESSAGE_NOT_FUNNY = '''Your submission breaks rule #5:

# MUST BE
# FUNNY
'''

def hour_valuation(hour_of_day : int):
    """
    Calculates a value relative to Reddit's activity patterns for a given hour.

    Parameters:
    hour_of_day (int): The hour of the day in 24-hour format.

    Returns:
    float: The valuation of the hour. Returns 0.8 if the hour is between 
    7pm and 7am EST, and 1.25 otherwise.
    """
    coefficent = 0.8

    # 7pm EST to 7am EST
    if hour_of_day < 12:
        return 1.0 * coefficent

    return 1.0 / coefficent

def discussion_score(submission : praw.models.Submission):
    """
    Calculates the discussion score of a submission by calculating the
    summation of the score of each comment.
    
    Parameters:
    submission (praw.models.Submission): The submission object.

    Returns:
    int: The discussion score of the submission.
    """

    # use .list() to flatten the comment tree
    # List[praw.models.Comment | praw.models.MoreComments]
    comments = submission.comments.list()

    # remove MoreComments objects
    # this is a simplification, but it should be good enough
    comments = [comment for comment in comments if isinstance(comment, praw.models.Comment)]

    return sum(comment.score for comment in comments)

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
    This is done to account for the varying levels of activity on Reddit at different times 
    of the day.

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

    _hours_ellapsed = _minutes_ellapsed / 60

    # 1 upvote per 10 minutes
    # 30 minutes = 3
    # 60 minutes = 6
    # 120 minutes = 12
    # 240 minutes = 24
    # 360 minutes = 36
    # 720 minutes = 72
    # 1440 minutes = 144
    base_target = math.floor(_minutes_ellapsed / 10)

    # Expect upvote rate to pick up after the first hour
    # 30 minutes = 1 + (0.5/12) = 1.0417
    # 60 minutes = 1 + (1/12) = 1.0833
    # 120 minutes = 1 + (2/12) = 1.1667
    # 240 minutes = 1 + (4/12) = 1.3333
    # 360 minutes = 1 + (6/12) = 1.5
    # 720 minutes = 1 + (12/12) = 2
    # 1440 minutes = 1 + (24/12) = 3
    hour_multiplier = 1 + (_hours_ellapsed / 12)

    # 30 minutes = 3 * 1.0417 = 3.125
    # 60 minutes = 6 * 1.0833 = 6.5
    # 120 minutes = 12 * 1.1667 = 14
    # 240 minutes = 24 * 1.3333 = 32
    # 360 minutes = 36 * 1.5 = 54
    # 720 minutes = 72 * 2 = 144
    # 1440 minutes = 144 * 3 = 432
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
        mod_note=submission_str(_submission)[:100]
    )
    _submission.mod.send_removal_message(
        type='public_as_subreddit',
        message=(REMOVAL_MESSAGE_NOT_FUNNY + submission_str(_submission))
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
    _minutes_ellapsed = adjusted_minutes_ellapsed(
        _submission.created_utc,
        minutes_ellapsed(_submission.created_utc)
    )

    # Don't remove submissions that are less than 1 hour old
    if _minutes_ellapsed < (1 * 60):
        return False

    # Don't remove submissions that are more than 4 hours old
    if _minutes_ellapsed > (4 * 60):
        return False

    _discussion_score = discussion_score(_submission)
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

    return allow_submission

def get_new_submissions(_reddit : praw.Reddit, limit : int):
    """
    Get the newest submissions from the subreddit.
    
    Parameters:
    _reddit (praw.Reddit): The Reddit instance.
    limit (int): The number of submissions to retrieve.

    Returns:
    praw.models.listing.generator.ListingGenerator: A generator that yields submission objects.
    """
    return _reddit.subreddit(SUBREDDIT_NAME).new(limit=limit)

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
    _discussion_score = discussion_score(_submission)
    _combined_score = _submission.score + _discussion_score
    _target_score = calculate_target(_adjusted_minutes_ellapsed)
    lines.append(f"id: {_submission.id}")
    # lines.append(f"title: {_submission.title[:20]}")
    lines.append(f"min: {_minutes_ellapsed}")
    lines.append(f"amin: {_adjusted_minutes_ellapsed}")
    lines.append(f"nc: {_submission.num_comments}")
    lines.append(f"sc: s{_submission.score}+d{_discussion_score}=c{_combined_score}")
    lines.append(f"ts: {_target_score}")
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

    # Print the action.__name__ to the console in yellow
    print(f"action: \033[93m{action.__name__}\033[0m")
    return None

def main(_reddit : praw.Reddit):
    """
    Loop through the newest submissions and evaluate them.

    Parameters:
    _reddit (praw.Reddit): The Reddit instance.

    Returns:
    None
    """
    for _submission in get_new_submissions(_reddit, 10):
        print(submission_str(_submission))
        evaluate_submission(_submission)
        print("----")
