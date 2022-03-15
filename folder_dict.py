from treelib import Node, Tree
import treetojson

import gdrive
import json

import config

class FolderDict(gdrive.Drive):

    # drive = gdrive.Drive().get_authenticated()

    def get_folder_id(self, root_folder_id, root_folder_title):
        file_list = gdrive.Drive().get_children(root_folder_id)
        for file in file_list:
            if(file['title'] == root_folder_title):
                return file['id']

    def add_children_to_tree(self, tree, file_list):
        for file in file_list:
            ext = file['mimeType'].split('.')[-1]
            if ext == 'folder':
                name = file['title']
            else:
                name = file['title'] + "." + ext

            # sys.exit()
            if file['mimeType'].__contains__('folder'):
                    download_Link = None
            else:
                if file['mimeType'].__contains__('google-apps'):
                    download_Link = file['exportLinks']
                else:
                    download_Link = file['webContentLink']

            tree['children'].extend(
                [{"name": file['title'], "type":ext, "id": file['id'], "parent_id":file['parents'][0]['id'], "view_link":file['alternateLink'], "download_link":download_Link, "date_created":file['createdDate']}])

    ### Recursion over all children ###
    def populate_tree_recursively(self, tree, parent_id):
        children = gdrive.Drive().get_children(parent_id)
        self.add_children_to_tree(tree, children)
        if(len(children) > 0):
            for child in children:
                self.populate_tree_recursively(tree, child['id'])

    ### Create tree and start populating from root ###
    def generate_tree(self, name):
        print('generating tree')
        root_folder_id = config.drive_id_info[name]

        tree = dict()

        tree = {"name": name, "type": "folder",
                "id": root_folder_id, "parent_id": None, "children": []}
        self.populate_tree_recursively(tree, root_folder_id)

        return tree

    def compare_and_update(self, name, new_fileList):
        with open(f'{name}.json', "r") as f:
            old_fileList = json.loads(f.read())
        # print(old_fileList)
        f = set()
        l = set()

        status = []
        added = False
        deleted = False
        for k in new_fileList['children']:
            print(k)
            f.add((k['name'], k['parent_id'], k['id'], k['type'], k['view_link'], str(k['download_link'])))
            # f.add({'name':k['name'], 'parent_id':k['parent_id'], 'file_id':f['id'], 'file_type': k['mimeType'].split('.')[-1]})
        for k in old_fileList['children']:
            l.add((k['name'], k['parent_id'], k['id'], k['type'], k['view_link'], str(k['download_link'])))

        if len(l - f) > 0:
            deleted = True
            status.append({'Deleted': l-f})
            print('Files have been deleted')

        if len(f - l) > 0:
            added = True
            status.append({'Added': f-l})
            print('New files have been added')

        if added or deleted:
            with open(f'{name}.json', 'w') as convert_file:
                convert_file.write(json.dumps(new_fileList, indent=4))

        return status, added, deleted

    def get_json(self, name):
        print(treetojson.get_json(data=self.generate_tree(name)))