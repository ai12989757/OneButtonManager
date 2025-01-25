import os
from datetime import datetime

def get_file_date(file_path):
    if '_' in file_path.split('.')[-1]:
        return file_path.split('.')[-1]  # 20250118_150204
    else:
        # 获取文件最后修改时间
        timestamp = os.path.getmtime(file_path)
        # 将时间戳格式化为日期字符串
        return datetime.fromtimestamp(timestamp).strftime('%Y%m%d_%H%M%S')

def getBackShelfList(path,fileType='mel'):
    # 根据保存备份的 mel 文件恢复 shelf
    shelf_backup = path

    fileDict = {}
    for file in os.listdir(shelf_backup):
        if file == 'shelf_copy.json' or file == 'shelf_recycle.json':
            continue
        if '.'+fileType in file:
            fileFath = shelf_backup + file
            name = file.split('.')[0].replace('shelf_', '')
            # 获取文件大小
            fileSize = os.path.getsize(shelf_backup + file)
            fileSize = round(fileSize / 1024, 2)
            data = get_file_date(fileFath)
            # 时间友好显示
            data = data[0:4] + '.' + data[4:6] + '.' + data[6:8] + ' ' + data[9:11] + ':' + data[11:13]
            if name not in fileDict.keys():
                fileDict[name] = []
            fileDict[name].append([name, data, fileSize,0,fileFath])

    fileList = []
    for i in fileDict.keys():
        if len(fileDict[i]) == 1:
            fileDict[i][0][3] = 1
            fileDict[i][0][2] = str(fileDict[i][0][2]) + 'KB'
            fileList.append(fileDict[i][0])
        else:
            tempSizeList = [j[2] for j in fileDict[i]]
            tempTimeList = [j[1] for j in fileDict[i]]

            if len(set(tempSizeList)) == 1:
                # 文件大小都一样时，比较 tempTimeList 里的值时间最新的
                max_index = tempTimeList.index(max(tempTimeList))
            else:
                # 文件大小不一样，比较 tempSizeList 里的值文件大小最大的
                max_index = tempSizeList.index(max(tempSizeList))

            fileDict[i][max_index][3] = 1

            for j in fileDict[i]:
                j[2] = str(j[2]) + 'KB'
                fileList.append(j)
    if fileType == 'json':
        return fileList
    for i in fileList:
        # 读取文件
        with open(i[4], 'r') as f:
            lines = f.readlines()
        fileData = ''.join(lines)
        if 'global proc' not in fileData or 'shelfButton' not in fileData:
            i[3] = 2

    return fileList