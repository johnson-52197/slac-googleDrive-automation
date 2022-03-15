import bot
import csv
import json
import config
import logging
from utils import utils
import folder_dict as fd
import gdrive


class Func():

    def __init__(self):
        drive = gdrive.Drive().get_authenticated()

    def createLog(self):
        logging.basicConfig(filename=f'log.log', format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S', filemode='w')
    @staticmethod
    def generate_subfolder_json():
        print('creating subfolder jsons')
        for folder in config.monitor:
            with open(f'{folder}.json', 'w') as f:
                f.write(json.dumps(fd.FolderDict().generate_tree(folder), indent = 4))

    def getChannelIDs(self):
        self.generate_Channel_ids()
        channels = config.channels
        for channel in channels:
            response = bot.client.chat_postMessage(channel = channel, text = 'Hi Everyone')
            row = [channel, response['channel']]
            utils.writeCSV('channelIDs', row)

    def generate_message_log(self):
        with open('messages.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['filename', 'filetype', 'id', 'parentID', 'postTime', 'folderName', 'channel_name', 'channel_id', 'message', 'attachment'])

    def generate_Channel_ids(self):
        with open('channelIDs.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['channelName', 'channelID'])

    @staticmethod
    def createFolderID_mapping(folders: list = config.monitor):
        print('Inside folder mapping creation')
        print('created subfolders')
        with open('folder.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['fileName', 'id', 'type', 'parentName', 'parentID', 'createdDate'])

        with open('folder.csv', 'a') as c:
            writer = csv.writer(c)
            for folder in folders:
                with open(f'{folder}.json', 'r') as j:
                    data = json.load(j)
                    parentID = data['id']
                    parentName = data['name']
                    if len(data['children']) > 0:
                        for file in (data['children']):
                            name = file['name']
                            fileID = file['id']
                            file_type = file['type']
                            createdDate = file['date_created']
                            row = [name, fileID, file_type, parentName, parentID, createdDate]
                            writer.writerow(row)

if __name__ == "__main__":
    obj = Func()
    obj.createLog()
    Func.generate_subfolder_json()
    obj.generate_message_log()
    Func.createFolderID_mapping()
    obj.getChannelIDs()
