from re import sub
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import config
import json
import pandas as pd
from utils import utils


class Drive:

    def get_object(self):
        return Drive.drive

    def get_authenticated(self):
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile("mycreds.txt")

        if gauth.credentials is None:
            # Authenticate if they're not there
            gauth.GetFlow()
            gauth.flow.params.update({'access_type': 'offline'})
            gauth.flow.params.update({'approval_prompt': 'force'})

            gauth.LocalWebserverAuth()

        elif gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()

        # Save the current credentials to a file
        gauth.SaveCredentialsFile("mycreds.txt")  
        Drive.drive = GoogleDrive(gauth)
        return Drive.drive

    def get_children(self, root_folder_id):
        str = "\'" + root_folder_id + "\'" + " in parents and trashed=false"
        file_list = Drive.drive.ListFile({'q': str}).GetList()
        return file_list

    def get_recent_configs(self):
        import config
        self.ROOT_FOLDER = config.ROOT_NAME
        self.ROOT_ID = config.ROOT_ID
        self.monitorList = config.monitor
        return

    def moveToTrash(self, id: str):
        file_obj = Drive.drive.CreateFile({'id': id})
        file_obj.Trash()

    def purgeOldFiles(self, channel_id: str, folder: str, subFolder: str):
        print('started purging')
        folderName = config.drive_slack_info[folder]
        df = utils.getFolderDF(folderName=folderName)
        if len(df)>0:
            # print(subFolder)
            parentID = df[(df['type'] == 'folder') & (df['name'] == subFolder)]['id'].values[0]
            df_files = df[df['parent_id'] == parentID]
            date = utils.gmt_datetime()
            df_files['days'] = df_files.apply(lambda row: utils.iso_time_difference_in_min(str(row['date_created'])[:-1], date), axis = 1)
            df_old = df_files[df_files['days']>=45]
            df_old.apply(lambda row: self.moveToTrash(row['id']), axis = 1)
            print('Done purging')
            return
        else:
            # bot.client.chat_postMessage(channel=channel_id, text="Folder doesn't exist")
            return 

    def deleteFile(self, id: str):
        file_obj = Drive.drive.CreateFile({'id': id})
        file_obj.Delete()
    
    def downloadFile(self, filename: str, ext: str, id: str):
        print('inside download')
        file_obj = Drive.drive.CreateFile({'id': id})
        print('created object')
        file_obj.GetContentFile(filename)


    def get_folder_id(self, name: str):
        fileList = self.drive.ListFile({'q': f"'{self.ROOT_ID}' in parents and trashed=false"}).GetList()
        for file in fileList:
            if(file['title'] == name):
                fileID = file['id']

    def create_subFolder(self, folderName: str, parentID: str):
        print('creating subfolder')
        print(folderName)
        print(parentID)
        folderlist = (self.drive.ListFile  ({'q': "mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList())

        titlelist =  [x['title'] for x in folderlist]
        if folderName in titlelist:
            for item in folderlist:
                if item['title'] == folderName:
                    return item['id']
    
        file_metadata = {
            'title': folderName,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [{"id": parentID}]  
        }

        folder = self.drive.CreateFile(file_metadata)
        folder.Upload()
        return folder['id']

    def moveToCompleted(self, channel_id:str, id: str):
        channel_name = utils.getChannelName(channelID=channel_id)
        print(channel_name)
        folderName = config.drive_slack_info[channel_name]
        print(folderName)
        df = utils.getFolderDF(folderName=folderName)
        print(df)
        completedFolderID = df[(df['type'] == 'folder') & (df['name'] == config.completed_folderName)]['id'].values[0]
        print(completedFolderID)
        file_obj = Drive.drive.CreateFile({'id': id})
        file_obj.Upload()
        print('Uploaded')
        file_obj['parents'] = [{"kind": "drive#parentReference", "id": completedFolderID}]
        print('uploaded to folder')
        file_obj.Upload()

    def moveFile(self, channel_name: str, file: str, folder: str):
        df_folder = pd.read_csv('folder.csv')
        # print(channel_name)
        df_folder = df_folder[df_folder['parentName'] == config.drive_slack_info[channel_name]]
        print(df_folder)
        # print(config.drive_slack_info[channel_name])
        # print(df_folder)
        masterFolderID = df_folder['parentID'].values[0]
        print('masterfolderid', masterFolderID)
        print(folder)
        print(type(df_folder.fileName))
        print(type(df_folder.fileName.tolist()))
        print(file)
        print(df_folder[df_folder['fileName'] == file])
        fileID = df_folder[df_folder['fileName'] == file]['id'].values[0]
        print(fileID)
        if folder in df_folder.fileName.tolist():
            print('Folder already exists')
            parentID = df_folder[df_folder['fileName'] == folder]['id'].values[0]
            print('creating file object ....')
            file_obj = Drive.drive.CreateFile({'id': fileID})
            print('done creating folder object')
            file_obj.Upload()
            file_obj['parents'] = [{"kind": "drive#parentReference", "id": parentID}]
            file_obj.Upload()
            return
        else:
            print('Doesnt exist - Creating...')
            parentID = self.create_subFolder(folderName=folder, parentID=masterFolderID)
            file_obj = Drive.drive.CreateFile({'id': fileID})
            file_obj.Upload()
            file_obj['parents'] = [{"kind": "drive#parentReference", "id": parentID}]
            file_obj.Upload()
            return

        return
            

    def monitor_folder(self):
        retrievedSet=set()
        fileList = self.drive.ListFile({'q': f"'{config.ROOT_ID}' in parents and trashed=false"}).GetList()
        for file in fileList:
            retrievedSet.add((file['title'],file['parents']['id']))

