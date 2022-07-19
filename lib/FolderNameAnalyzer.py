import os
import csv
import time
import subprocess
import yaml
app_home = os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)) , ".." ))

class FolderNameAnalyzer:
    def __init__(self, features):
        self.features = features

    # 仮想フォルダ単位で，ファイルアクセス履歴の拡張子を用いてフォルダ名を付与
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
        folder_name = self.folder_name_using_extension_database(sort_wds_extensions, work_content_num=1)[0]
        return folder_name

    # 仮想フォルダにあるWD単位で，ファイルアクセス履歴の拡張子を用いてフォルダ名を付与
    def virtual_folder_name_analyze2(self, working_directorys):
        foldername_list = {}
        for wd in working_directorys:
            wd_extensions = {}
            ext_groups = self.features[wd]
            for ext_group in ext_groups:
                ext = ext_group.split("TO")[0]
                if wd_extensions.get(ext):
                    wd_extensions[ext] += 1
                else:
                    wd_extensions[ext] = 1
            sort_wd_extensions = sorted(wd_extensions.items(), key=lambda x:x[1], reverse=True)
            foldername_tmp = self.folder_name_using_extension_database(sort_wd_extensions, work_content_num=1)[0]
            if foldername_list.get(foldername_tmp):
                foldername_list[foldername_tmp] += 1
            else:
                foldername_list[foldername_tmp] = 1
        sort_foldername_list = sorted(foldername_list.items(), key=lambda x:x[1], reverse=True)
        foldername = list(sort_foldername_list)[0][0]
        return foldername

    # 仮想フォルダ単位で，静的ファイルの拡張子を用いてフォルダ名を付与
    def virtual_folder_name_analyze3(self, working_directorys):
        wds_list = ""
        for wd in working_directorys:
            wds_list = wds_list + wd + " "
        output = subprocess.check_output("find " + str(wds_list) + "-type f | awk -F. '{print $NF}' | sort | uniq -c | sort -nr | awk -F ' ' '{print $NF}'",  shell=True, text=False)
        exts = output.decode().split("\n")
        try:
            del exts[30:]
        except:
            pass
        foldername = self.folder_name_using_extension_database(exts, work_content_num=1)[0]
        return foldername

    # 仮想フォルダにあるWD単位で，，静的ファイルの拡張子を用いてフォルダ名を付与
    def virtual_folder_name_analyze4(self, working_directorys):
        wds_list = ""
        foldername_list = {}
        for wd in working_directorys:
            wds_list = wds_list + wd + " "
            output = subprocess.check_output("find " + str(wd) + " -type f | awk -F. '{print $NF}' | sort | uniq -c | sort -nr | awk -F ' ' '{print $NF}'",  shell=True, text=False)
            exts = output.decode().split("\n")
            try:
                del exts[30:]
            except:
                pass

            foldername_tmp = self.folder_name_using_extension_database(exts, work_content_num=1)[0]
            if foldername_list.get(foldername_tmp):
                foldername_list[foldername_tmp] += 1
            else:
                foldername_list[foldername_tmp] = 1
        sort_foldername_list = sorted(foldername_list.items(), key=lambda x:x[1], reverse=True)
        foldername = list(sort_foldername_list)[0][0]
        return foldername

    def working_directorys_extensions(self, working_directorys, wds_extensions):
        with open(app_home + "/db/working_directorys_extensions.csv", "a") as f:
            f.write(str(working_directorys) + "," + str(wds_extensions) + "\n")

    def working_directory_extensions(self, working_directory, extensions):
        with open(app_home + "/db/working_directory_extensions.csv", "a") as f:
            f.write(str(working_directory) + "," + str(extensions) + "\n")

    # 拡張子が一番多いものから順にデータベースと照合し，フォルダ名を付与
    def folder_name_using_extension_database(self, wds_extensions, *, work_content_num = yaml.load(open(app_home + '/settings.yml','r'), Loader=yaml.SafeLoader)['SEMANTIC_FILE_SETTINGS']['work_content_num']
):
        work_content_list = []
        with open(app_home + "/db/extension_db.csv", "r") as f:
            reader = csv.reader(f)
            dbs = list(reader)
            i = 0
            for wds_extension in list(wds_extensions):
                i+=1
                for db in dbs:
                    if wds_extension[0] == db[0]:
                        work_content_list.append(db[1])
                        if len(work_content_list) >= work_content_num:
                            return work_content_list

        if work_content_list == []:
            work_content_list.append("None")

        return work_content_list
