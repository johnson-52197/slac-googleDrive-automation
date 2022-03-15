# Slack - Drive Integration
### 1. install requiements
```
pip install -r requirements.txt
```

### 2. Edit .env file
```
Create a slack bot get the SLACK_TOKEN and SIGNING_SECRET (run 'bot.py' when setting up event subscription)
Follow this tutorial for reference: https://www.youtube.com/watch?v=KJ5bFv-IRFM 
Bot Permissions/Events: 
-> messages.channels
-> reaction_added

Add your slack bot to all your slack channels 
    - Click on the channel name on the top
    - Click Integration -> Add apps -> Select your bot
```

### 3. Create a project on Google Console
```
1. Follow this tutorial and generate the JSON file. https://medium.com/analytics-vidhya/pydrive-to-download-from-google-drive-to-a-remote-machine-14c2d086e84e (You just need to generate the client_secrets.json and others are not necessary)
```

### 4. Edit config.py
```
1. Refer the comments on config.py
```

### 5. Slack API
```
1. Follow the above video and setup the slack event subscription and slash commands
2. Slash commands are "/move", "/purge"
```

### 6. After completing all the steps, run 'setup.py' once.

### 7. Commands
```
1. /purge <foldername> 
    (example: /purge Sales)
    Purge command deletes all the files older than 45 days in the folder in which the slack channel is associated with. 
2. /move <filename> to <foldername> 
    (example: /move invoice.pdf to Sales)
    Move command works within the slack associated folder
3. show-tree (not a slash command)
    show-tree command show the folder tree for the specific channel related folder
```

### 8. View, Download, Mark as Completed, Assign to User, Submit Query
```
Whenever a new file is added, a message will be posted on the folder specific channel and data entry channel
That message will contain view(button), download as xxxx(button) only.

To achieve Mark as completed task, 
Emoji tick mark should be used. 
This will move the file to Entered Invoices folder(considered as completed folder, can be changed in config.py) within the channel specific folder.

To achieve assign to user task,
Mention the person on the message thread.
This will delete the post from data entry and current channel and post it to pending tasks channel.
```

Pending Tasks:

Submit query is yet to be implemented - Need clarity
Temporary logs are implemented - Need more clarity on what actions and fields needs to be stored.