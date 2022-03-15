IP = "191.xx.xx.xx" # Enter you server IP address
port = 5001 # Enter your port number

channels = ['arnies-barn', 'beast-and-barrel', 'belt-sports-complex', '_data_entry', '_pending_tasks']
monitor = ["Arnie's Barn", "Beast & Barrel", "Belt Sports Complex"] # Folder to monitor

# slack group name : associated folder name
drive_slack_info = {
    "arnies-barn": "Arnie's Barn",
    "beast-and-barrel": "Beast & Barrel",
    "belt-sports-complex": "Belt Sports Complex",
}

# folder name: associated slack channel name
slack_drive_info = {
    "Arnie's Barn": "arnies-barn",
    "Beast & Barrel": "beast-and-barrel",
    "Belt Sports Complex": "belt-sports-complex"
}


# folder name : folder id
# folder IDs can be found on the google drive url
# https://drive.google.com/drive/folders/1Qmk7ZMWfFToTj5fwb9EiiVz9tir_-jc1
# each folder will have different folder IDs
# Enter only the main folder IDs (channel specific folders)
drive_id_info = {
    "Arnie's Barn": '1Qmk7ZMWfFToTj5fwb9EiiVz9tir_-jc1',
    "Beast & Barrel": '1kDBVKTS4Y7UGJZ6_f3TBUDAsIop40lGR',
    "Belt Sports Complex" : '1k1qUwnveEEMQlRLAyAePGulKpR32_NnS'
}

ROOT_NAME = "mosaic" # Root folder name
ROOT_ID = "1l_e8BRyjx1lAsdnvNVArsbK9cxkfFpkU" # Root Folder ID

completed_folderName = 'Entered Invoices'
file_added_msg = 'New File added'
file_deleted_msg = 'File has been deleted'
file_added_attachment = [
        {
            "text": "",
            "fallback": "You are unable to choose an option",
            "callback_id": "callback_id",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "view",
                    "text": "View",
                    "type": "button",
                    "value": "view",
                    "url": ""
                }
            ]
        }
    ]
