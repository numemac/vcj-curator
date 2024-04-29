# Vegancirclejerk-Python

This is a bot that uses the Reddit API to moderate the r/vegancirclejerk subreddit, which has over 100k members.

## Installation

The bot is set to run every 30 minutes on Linux. The following instructions have been tested on Arch Linux.

### Step 1: Create a Reddit 'script' app

1. Go to `https://www.reddit.com/prefs/apps`.
2. Set the `name` to `vcj_mod_bot`.
3. Set the `description` to `helps moderate r/vegancirclejerk (100k users)`.
4. Set the `about url` and `redirect uri` to `https://www.reddit.com/message/compose?to=/r/vegancirclejerk`.
5. Press `create app`.
6. Note that `REDDIT_CLIENT_ID` is under `personal use script`.
7. Note that `REDDIT_CLIENT_SECRET` is labeled as `secret` after pressing edit on your app.

### Step 2: Clone the repository

```git clone git@github.com:ryan-augustinsky/vegancirclejerk-python.git```

### Step 3: Configure the service

1. Copy the example service:

```cp vegancirclejerk-python/systemd/example.vegancirclejerk.service vegancirclejerk-python/systemd/vegancirclejerk.service```

2. Edit the service with your favourite editor, e.g., ```vi vegancirclejerk-python/systemd/vegancirclejerk.service.```
- **WARNING:** Putting your credentials in plain text is dangerous, consider using a secrets manager.
- Use the `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` from step 1.
- Set your `REDDIT_USERNAME` and `REDDIT_PASSWORD` to match your mod account's info.
- Be sure to replace the `/EXAMPLE/PATH`
- Be sure to replace the `EXAMPLE_YOUR_USER` with your linux user name

### Step 4. Set up systemd

1. Copy or symlink your `vegancirclejerk.service` file to `~/.config/systemd/user/`.
```
ln -s vegancirclejerk-python/systemd/vegancirclejerk.service ~/.config/systemd/user/
ln -s vegancirclejerk-python/systemd/vegancirclejerk.timer ~/.config/systemd/user/
```

2. Enable and start the service and timer:
```
systemctl --user enable vegancirclejerk.timer
systemctl --user enable vegancirclejerk.service
systemctl --user start vegancirclejerk.timer
```

### Step 5. Verify the service

Check that the service and timer are running:

```
systemctl --user status vegancirclejerk.timer
systemctl --user status vegancirclejerk.service
```