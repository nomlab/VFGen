import os
import csv
app_home = os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)) , ".." ))

class FolderNameAnalyzer:
    def __init__(self, features):
        self.features = features

    def virtual_folder_name_analyze(self, working_directorys):
        wds_extensions = {}
        for wd in working_directorys:
            wd_extensions = {}
            ext_groups = self.features[wd]
            for ext_group in ext_groups:
                ext = ext_group.split("TO")[0]
                if wds_extensions.get(ext):
                    wds_extensions[ext] += 1
                else:
                    wds_extensions[ext] = 1
                if wd_extensions.get(ext):
                    wd_extensions[ext] += 1
                else:
                    wd_extensions[ext] = 1
            sort_wd_extensions = sorted(wd_extensions.items(), key=lambda x:x[1], reverse=True)
            #self.working_directory_extensions(wd, sort_wd_extensions)
        sort_wds_extensions = sorted(wds_extensions.items(), key=lambda x:x[1], reverse=True)
        self.working_directorys_extensions(working_directorys, sort_wds_extensions)
        folder_name = self.folder_name_using_extension_database(sort_wds_extensions)
        return folder_name

    def working_directorys_extensions(self, working_directorys, wds_extensions):
        with open(app_home + "/db/working_directorys_extensions.csv", "a") as f:
            f.write(str(working_directorys) + "," + str(wds_extensions) + "\n")

    def working_directory_extensions(self, working_directory, extensions):
        with open(app_home + "/db/working_directory_extensions.csv", "a") as f:
            f.write(str(working_directory) + "," + str(extensions) + "\n")

    def folder_name_using_extension_database(self, wds_extensions):
        with open(app_home + "/db/extension_db.csv", "r") as f:
            reader = csv.reader(f)
            dbs = list(reader)
            i = 0
            for wds_extension in list(wds_extensions):
                i+=1
                for db in dbs:
                    if wds_extension[0] == db[0]:
                        return db[1]
        return "None"
