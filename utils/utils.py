import csv
import json
import config
import pandas as pd
from gspread_pandas import Spread
from datetime import datetime as dt, timedelta

def getChannelID(channelName: str):
    df = pd.read_csv('channelIDs.csv')
    channel_id = df[df['channelName'] == channelName]['channelID'].values[0]
    return channel_id

def getChannelName(channelID: str) -> str:
    df_id = pd.read_csv('channelIDs.csv')
    channel_name = df_id[df_id['channelID'] == channelID]['channelName'].values[0]
    return channel_name

def getFolderDF(folderName: str) -> pd.DataFrame:
    f = open(f'{folderName}.json')
    df = pd.DataFrame(json.load(f)['children'])
    return df

def gmt_datetime() -> str:
    """Return current gmt time in ISO format YYY-MM-DDThh:mm:ss"""
    # return dt.utcnow().isoformat("T", "milliseconds")+'Z'
    return dt.utcnow().isoformat()

def logData():
    x= Spread('test', 'Sheet2')
    df = pd.read_csv('log.csv')
    x.df_to_sheet(df, index=False, sheet='Sheet1', replace=True)

def writeCSV(fileName: str, row: list):
    with open(f'{fileName}.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(row)

def iso_time_difference_in_min(t1: str, t2: str) -> float:
    """Returns difference between ISO time strings in minutes, with 2-decimal resolution"""
    print(t1, t2)
    dt1 = dt.fromisoformat(t1)
    dt2 = dt.fromisoformat(t2)
    if dt1 > dt2:
        td = dt1 - dt2
    else:
        td = dt2 - dt1

    diff_min = round(td.total_seconds() // (24 * 3600), 2)
    return diff_min

def refreshFoldersCSV():
    with open('folder.csv', 'a') as c:
        writer = csv.writer(c)
        for folder in config.monitor:
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
    