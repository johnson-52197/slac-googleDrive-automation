from treelib import Node, Tree
import treetojson

import gdrive

class FolderTree(gdrive.Drive):
    ### Helper functions ### 
    
    def get_folder_id(self, root_folder_id, root_folder_title):
        file_list = gdrive.Drive().get_children(root_folder_id)
        for file in file_list:
            if(file['title'] == root_folder_title):
                return file['id']

    def add_children_to_tree(self, tree, file_list, parent_id):
        for file in file_list:
            ext = file['mimeType'].split('.')[-1]
            if ext == 'folder':
                name = file['title']
            else:
                name = file['title'] + "." + ext
            tree.create_node(name, file['id'], parent=parent_id)
        
    ### Recursion over all children ### 
    def populate_tree_recursively(self, tree, parent_id):
        children = gdrive.Drive().get_children(parent_id)
        self.add_children_to_tree(tree, children, parent_id)
        if(len(children) > 0):
            for child in children:
                self.populate_tree_recursively(tree, child['id'])

    ### Create tree and start populating from root ###
    def show_tree(self, name: str, id: str):
        root_folder_title = name
        # root_folder_id = self.get_folder_id("root", root_folder_title)
        root_folder_id = id
        tree = Tree()
        tree.create_node(root_folder_title, root_folder_id)
        self.populate_tree_recursively(tree, root_folder_id)
        return tree

    def get_json(self, name):
        print(treetojson.get_json(data=self.show_tree(name)))
