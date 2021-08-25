import yaml
import os
app_home = os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)) , ".." ))

try:
    settings = yaml.load(open(app_home + '/settings.yml','r'), Loader=yaml.SafeLoader)
except:
    print("Error: Cannnot open log file. Check your settings.")
    logger.error("Cannnot open log file. Check your settings.")
    sys.exit()

logfile = settings['ACCESS_LOG_FILE_PATH']
f = open(logfile, "r")

read_log_num = 0
equal_log_num = 0
not_update_log_num = 0
error_log_num = 0
log1 = f.readline()
path = log1.split(",")[1]
filename = path.split("/")[-1]
extensions = {}
if ("." in filename):
    ext = filename.split(".")[-1]
    extensions[ext] = 1
    read_log_num += 1

while len(log1) > 0:
    try:
        log2 = f.readline()
        if log1 != log2:
            log1 = log2
            data = log1.split(",")
            path = data[-2]
            event = data[-1]
            filename = path.split("/")[-1]
            if (("." in filename) & (("Created" in event) | ("Updated" in event))):
                ext = filename.split(".")[-1]
                read_log_num += 1
                if extensions.get(ext):
                    extensions[ext] += 1
                else:
                    extensions[ext] = 1
            else:
                not_update_log_num += 1
        else:
            equal_log_num += 1
    except:
        # print(log1)   # エラーがあったファイルアクセス履歴を見る際に使用
        error_log_num += 1

print("read_log_num :\t"+str(read_log_num))
print("not_update_log_num :\t"+str(not_update_log_num))
print("equal_log_num :\t"+str(equal_log_num))
print("error_log_num :\t"+str(error_log_num-1)+"\n")

write_file = open(app_home + "/db/extension.csv", "w")
sort_extentsions = sorted(extensions.items(), key=lambda x:x[1], reverse=True)
count = 0
for ext in sort_extentsions:
    count += ext[1]
    write_file.write(str(ext[0])+","+str(ext[1])+"\n")
