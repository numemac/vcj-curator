"""
"""

import praw
import prawcore

VCJ_SUBREDDIT_NAME = 'vegancirclejerk'
VCJC_SUBREDDIT_NAME = 'vegancirclejerkchat'

def select_submission(_reddit):
    """
    """
    # select the top submission of the week from VCJC
    _vcjc_subreddit = _reddit.subreddit(VCJC_SUBREDDIT_NAME)
    _vcjc_submissions = _vcjc_subreddit.top('week', limit=1)
    _vcjc_submission = next(_vcjc_submissions)
    return _vcjc_submission

def crosspost_submission(_reddit, _submission):
    """
    """
    _vcj_subreddit = _reddit.subreddit(VCJ_SUBREDDIT_NAME)

    # crosspost the VCJC submission to the VCJ subreddit
    _xpost = _submission.crosspost(subreddit=_vcj_subreddit, send_replies=False, flair_id="2957c1f8-092f-11ef-bfd0-7accde59c924")
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

def remove_crosspost_sticky(_reddit, _excluded_submission):
    """
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
            return None

    # if the sticky is a crosspost of the excluded submission, don't remove it
    if _sticky.url == _excluded_submission.url:
        return None

    _sticky.mod.sticky(state=False)

    # delete the sticky post if it was authored by the bot
    if _sticky.author.name == _reddit.user.me().name:
        _sticky.delete()
        print(f'Removed sticky post: _sticky.id={_sticky.id}, _sticky.title={_sticky.title}')

def main(_reddit: praw.Reddit):
    """
    """
    _submission = select_submission(_reddit)
    remove_crosspost_sticky(_reddit, _submission)
    _crosspost = crosspost_submission(_reddit, _submission)
    print(f'Managing crosspost of submission: id={_submission.id}, title={_submission.title}')
    return None
