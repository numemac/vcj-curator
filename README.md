# vegancirclejerk-python
A bot that uses the Reddit API to moderate the r/vegancirclejerk subreddit (100k members).

## Installation to run every 30 minutes on Linux (tested with Arch Linux)
1. Create a Reddit 'script' app at `https://www.reddit.com/prefs/apps`. 
- Set the `name` to `vcj_mod_bot`
- Set the `description` to `helps moderate r/vegancirclejerk (100k users)`
- Set the `about url` to `https://www.reddit.com/message/compose?to=/r/vegancirclejerk`
- Set the `redirect uri` to `https://www.reddit.com/message/compose?to=/r/vegancirclejerk`
- Press `create app`
- Note that `REDDIT_CLIENT_ID` is under `personal use script`
- Note that `REDDIT_CLIENT_SECRET` is labeled as `secret` after pressing edit on your app.
2. Clone the repo `git clone git@github.com:ryan-augustinsky/vegancirclejerk-python.git`
3. Copy the example service to one you will configure `cp vegancirclejerk-python/systemd/example.vegancirclejerk.service vegancirclejerk-python/systemd/vegancirclejerk.service`
4. Edit the service with your favourite editor, e.g. `vi vegancirclejerk-python/systemd/vegancirclejerk.service`
- Use the `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` from step 1.
- Set your `REDDIT_USERNAME` and `REDDIT_PASSWORD` to match your mod account's info.
- WARNING: Putting your credentials in plain text is dangerous, consider using a secrets manager.
- Be sure to replace the `/EXAMPLE/PATH`
- Be sure to replace the `EXAMPLE_YOUR_USER` with your linux user name
5. Copy or symlink your `vegancirclejerk.service` file to `~/.config/systemd/user/`.
- `ln -s vegancirclejerk-python/systemd/vegancirclejerk.service ~/.config/systemd/user/`
- `ln -s vegancirclejerk-python/systemd/vegancirclejerk.timer ~/.config/systemd/user/`
6. Do the same for `vegancirclejerk.timer`
7. Run
- `systemctl --user enable vegancirclejerk.timer`
- `systemctl --user enable vegancirclejerk.service`
- `systemctl --user start vegancirclejerk.timer`
8. Verify that it's running by using 
- `systemctl --user status vegancirclejerk.timer`
- `systemctl --user status vegancirclejerk.service`