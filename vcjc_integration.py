"""
vcjc_integration.py
"""

import praw
import prawcore
from constants import UNJERK_FLAIR, VCJ_SUBREDDIT_NAME, VCJC_SUBREDDIT_NAME

def select_submission(_reddit):
    """
    Select the top submission of the week from the VCJC subreddit.

    Parameters:
    _reddit (praw.Reddit): The Reddit instance.

    Returns:
    praw.models.Submission: The selected submission.
    """
    _vcjc_subreddit = _reddit.subreddit(VCJC_SUBREDDIT_NAME)
    _vcjc_submissions = _vcjc_subreddit.top('week', limit=1)
    _vcjc_submission = next(_vcjc_submissions)
    return _vcjc_submission

def crosspost_submission(_reddit, _submission):
    """
    Crosspost the submission to the VCJ subreddit.
    Comment a link to the original sumission.
    Distinguish the comment and then lock the crosspost.

    Parameters:
    _reddit (praw.Reddit): The Reddit instance.
    _submission (praw.models.Submission): The submission to crosspost.

    Returns:
    praw.models.Submission: The crossposted submission.
    """
    _vcj_subreddit = _reddit.subreddit(VCJ_SUBREDDIT_NAME)

    # crosspost the VCJC submission to the VCJ subreddit
    _xpost = _submission.crosspost(subreddit=_vcj_subreddit, send_replies=False, flair_id=UNJERK_FLAIR)
    print(f'Created new crosspost submission: _xpost.id={_xpost.id}')

    # sticky the crossposted submission
    _xpost.mod.sticky(bottom=True)

    # comment the link to the crossposted submission in the VCJC submission
    _xpost_comment = _xpost.reply(f'### Continue to the discussion [here]({_submission.url}).')

    # distinguish the xpost comment
    _xpost_comment.mod.distinguish()

    # lock the VCJ crosspost submission comments
    _xpost.mod.lock()

    return _xpost

def remove_crosspost_sticky(_reddit, _excluded_title):
    """
    Remove the sticky post if it is not a crosspost of the excluded submission.

    Parameters:
    _reddit (praw.Reddit): The Reddit instance.
    _excluded_title (str): Don't remove the sticky if it has this title.

    Returns:
    bool: True if the sticky post was removed, False otherwise. True if the sticky post was not found.
    """
    _vcj_subreddit = _reddit.subreddit(VCJ_SUBREDDIT_NAME)
    _sticky = None

    try:
        _sticky = _vcj_subreddit.sticky(2)
    except prawcore.exceptions.NotFound:
        # continue and try sticky 1
        pass

    if _sticky is None:
        try:
            _sticky = _vcj_subreddit.sticky(1)
        except prawcore.exceptions.NotFound:
            return True

    # if the sticky is a crosspost of the excluded submission, don't remove it
    if _sticky.title == _excluded_title:
        return None

    _sticky.mod.sticky(state=False)

    # delete the sticky post if it was authored by the bot
    if _sticky.author.name == _reddit.user.me().name:
        _sticky.delete()
        print(f'Removed sticky post: _sticky.id={_sticky.id}, _sticky.title={_sticky.title}')

        return True
    
    return False

def main(_reddit: praw.Reddit):
    """
    Manage the crosspost of the top submission of the week from the VCJC subreddit.

    Parameters:
    _reddit (praw.Reddit): The Reddit instance.

    Returns:
    None
    """
    _submission = select_submission(_reddit)
    if remove_crosspost_sticky(_reddit, _submission.title):
        crosspost_submission(_reddit, _submission)
    print(f'Managing crosspost of submission: id={_submission.id}, title={_submission.title}')
    return None
