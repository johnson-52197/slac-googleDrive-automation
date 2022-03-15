import logging
import slack
import os
import time
import config
import pandas as pd
from pathlib import Path
# from dotenv import load_dotenv
from flask import Flask, request, Response, after_this_request
from slackeventsapi import SlackEventAdapter
import gdrive
from utils import utils
import folder_tree as ft
import folder_dict as fd

# env_path = Path(".") / ".env"
# load_dotenv(dotenv_path=env_path) 


logging.basicConfig(filename=f'log.log', format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S', filemode='a')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)

# slack_events_adapter = SlackEventAdapter(
#     os.environ['SIGNING_SECRET'], '/slack/events', app)

slack_events_adapter = SlackEventAdapter(
    SIGNING_SECRET, '/slack/events', app)

client = slack.WebClient(token=SLACK_TOKEN)
BOT_ID = client.api_call('auth.test')['user_id']


def monitorFolder(folder: str):
    new_fileList = fd.FolderDict().generate_tree(folder)
    status, added, deleted = fd.FolderDict().compare_and_update(folder, new_fileList)
    parent_id = config.drive_id_info[folder]
    # TODO : Implement proper preprocessing before sending it to slack
    return status, added, deleted, parent_id


def removeandPost(removeFrom: str, postTo: str, ts: str):
    logger.info('Request to remove post, Remove from: ' + str(utils.getChannelName(
        removeFrom)) + ', Post to: ' + str(postTo) + ', Message time: ' + ts)
    df = pd.read_csv('messages.csv')
    message = df[df['postTime'].astype(str) == ts]['message'].values[0]
    attachement = df[df['postTime'].astype(str) == ts]['attachment'].values[0]
    df = df[~(df['postTime'].astype(str) == ts)]
    df.to_csv('messages.csv', index=False)
    attachement = eval(attachement)
    client.chat_postMessage(channel='_pending_tasks',
                            text=message, attachments=attachement)
    client.chat_delete(channel=removeFrom, ts=str(ts))
    logger.info('Removed and reposted!')
    return


def removePOST(channel_name: str, ts: float):
    logger.info('Request to remove post, Remove from: ' + channel_name)
    channelID = utils.getChannelID(channelName=channel_name)
    df_messages = pd.read_csv('messages.csv')
    df_messages['postTimeINT'] = df_messages['postTime'].astype(int)
    ts = int(ts)
    ts_list = [ts+i for i in range(1, 5)]
    msg_time = df_messages[(df_messages['postTimeINT'].isin(
        ts_list))]['postTime'].values[0].astype(str)
    df_messages = df_messages[~(df_messages['postTimeINT'].isin(ts_list))]
    client.chat_delete(channel=channelID, ts=str(msg_time))
    df_messages.to_csv('messages.csv', index=False)
    logger.info('Post removed!')
    return


def fileadded(details, folderName: str):
    file_name = list(details)[0][0]
    parent_id = list(details)[0][1]
    file_id = list(details)[0][2]
    ext = list(details)[0][3]
    viewLink = list(details)[0][4]

    f = config.file_added_attachment

    try:
        downloadLink = eval(list(details)[0][5])
        if len(downloadLink) > 1:
            l = []
            for ext, link in downloadLink.items():
                download_as = ext.split('/')[-1]
                additional_downloadLinks = {
                    "name": f"download_{ext}", "text": f'Download as {download_as}', "type": "button", "value": f"value_{ext}", "url": link}
                l.append(additional_downloadLinks)
                f[0]['actions'].append(additional_downloadLinks)
    except:
        downloadLink = list(details)[0][5]
        download_as = ext.split('/')[-1]
        additional_downloadLinks = {"name": f"download_{ext}", "text": f'Download as {download_as}',
                                    "type": "button", "value": f"value_{ext}", "url": downloadLink}
        f[0]['actions'].append(additional_downloadLinks)

    message = config.file_added_msg + \
        f"\nFILE NAME: {file_name} \nFILE TYPE: {ext} \n"
    f[0]['actions'][0]['url'] = viewLink

    channel_name = config.slack_drive_info[folderName]
    channel_id = utils.getChannelID(channelName=channel_name)
    dataentryID = utils.getChannelID(channelName='_data_entry')

    response = client.chat_postMessage(
        channel=channel_name, text=message, attachments=f)
    utils.writeCSV(fileName='messages', row=[
                   file_name, ext, file_id, parent_id, response['ts'], folderName, channel_name, channel_id, message, f])
    time.sleep(1)
    response = client.chat_postMessage(
        channel='_data_entry', text=message, attachments=f)
    utils.writeCSV(fileName='messages', row=[
                   file_name, ext, file_id, parent_id, response['ts'], folderName, '_data_entry', dataentryID, message, f])

    return


def fileDeteted(details, folderName: str):
    file_name = list(details)[0][0]
    ext = list(details)[0][3]
    message = config.file_deleted_msg + \
        f"\nFILE NAME: {file_name} \nFILE TYPE: {ext}"
    channel_id = config.slack_drive_info[folderName]
    client.chat_postMessage(channel=channel_id, text=message)
    return


def showTree(channelName: str, folderName: str, folderID: str):
    text = ft.FolderTree().show_tree(name=folderName, id=folderID)
    client.chat_postMessage(channel=channelName, text=str(text))
    return


def driveMonitor():
    logger.info('Monitoring Folder')
    for folder in config.monitor:
        status, added, deleted, parent_id = monitorFolder(folder)
        changed_files = len(status)
        for file in status:
            if 'Added' in file.keys():
                fileadded(file['Added'], folderName=folder)
            if 'Deleted' in file.keys():
                fileDeteted(file['Deleted'], folderName=folder)

    return


@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
    emoji = event_data["event"]["reaction"]
    if emoji == 'white_check_mark':
        ts = event_data['event']['item']['ts']
        channel_id = event_data['event']['item']['channel']
        removePOST(channel_name='_data_entry', ts=float(ts))
        df = pd.read_csv('messages.csv')
        row = df[df['postTime'].astype(str) == str(ts)]

        @after_this_request
        def add_close_action(response):
            @response.call_on_close
            def process_after_request():
                gdrive.Drive().moveToCompleted(
                    channel_id=channel_id, id=str(row['id'].values[0]))
                df.drop(row.index, inplace=True)
                df.to_csv('messages.csv', index=False)
                logger.info('Marked as completed')
            return response
        return Response(), 200

    else:
        pass


@slack_events_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if text == 'monitor':
        @after_this_request
        def add_close_action(response):
            @response.call_on_close
            def process_after_request():
                driveMonitor()
            return response
        return Response(), 200

    if user_id != BOT_ID:
        if text == 'show-tree':

            channel_name = utils.getChannelName(channelID=channel_id)
            folderName = config.drive_slack_info[channel_name]
            folderID = config.drive_id_info[folderName]

            @after_this_request
            def add_close_action(response):
                @response.call_on_close
                def process_after_request():
                    showTree(folderName=folderName, folderID=folderID,
                             channelName=channel_name)
                return response
            return Response(), 200

        elif text.startswith('<@') and 'thread_ts' in event.keys():
            df = pd.read_csv('messages.csv')
            thread_ts = event.get('thread_ts')
            if thread_ts in df['postTime'].astype(str).tolist():

                @after_this_request
                def add_close_action(response):
                    @response.call_on_close
                    def process_after_request():
                        removeandPost(removeFrom=channel_id,
                                      postTo='_pending_tasks', ts=thread_ts)
                    return response
                return Response(), 200

    return


@app.route("/purge", methods=['GET', 'POST'])
def test():
    data = request.form
    channel_name = data.get('channel_name')
    channel_id = data.get('channel_id')
    text = data.get('text')

    @after_this_request
    def add_close_action(response):
        @response.call_on_close
        def process_after_request():
            gdrive.Drive().purgeOldFiles(channel_id=channel_id,
                                         folder=channel_name, subFolder=text)
        return response
    return Response(), 200


@app.route('/move', methods=['POST'])
def move():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    channel_name = data.get('channel_name')
    text = data.get('text')
    text = text.split(' to ')
    file = text[0].strip()
    folder = text[-1].strip()

    @after_this_request
    def add_close_action(response):
        @response.call_on_close
        def process_after_request():
            gdrive.Drive().moveFile(channel_name=channel_name, file=file, folder=folder)
        return response
    return Response(), 200


@app.route('/message-count', methods=['POST'])
def message_count():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    text = data.get('text')
    client.chat_postMessage(channel=channel_id, text='I got the command')
    return Response(), 200


# if __name__ == "__main__":
#     drive = gdrive.Drive().get_authenticated()
#     host = config.IP
#     port = config.port
#     app.run(debug=False, host=host, port=port, use_reloader=False)


if __name__ == "__main__":
    drive = gdrive.Drive().get_authenticated()
    app.run()
 