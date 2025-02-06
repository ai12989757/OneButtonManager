# -*- coding: utf-8 -*-
import os
import json
import codecs
from collections import OrderedDict

def getGIFButtonData(button):
    # 获取按钮数据
    data = OrderedDict()
    data['label'] = button.labelText
    data['annotation'] = button.annotation
    data['image'] = button.iconPath
    data['command'] = button.command
    data['size'] = button.size
    data['menuItem'] = OrderedDict()

    for index, i in enumerate(button.menu.actions()):
        menuData = OrderedDict()
        if i.__class__.__name__ == 'Separator':
            data['menuItem'][index] = 'separator'
        elif i.__class__.__name__ == 'gifIconMenuAction':
            menuData['label'] = i.label
            menuData['command'] = i.command
            menuData['annotation'] = i.annotation
            menuData['image'] = i.iconPath
            data['menuItem'][index] = menuData
    return data

def copyButton(button, path=None):
    path = path + 'shelf_copy.json'
    # 在 Python 2.7 中，open 函数不支持 encoding 参数。你需要使用 codecs 模块来处理文件的编码。
    if not os.path.exists(path):
        with codecs.open(path, 'w', 'utf-8') as f:
            json.dump({"shelfName": "buttonEdit", "shelfData": {}}, f, indent=4, ensure_ascii=False)

    buttonData = getGIFButtonData(button)
    jsonData = {"shelfName": "buttonEdit", "shelfData": buttonData}

    with codecs.open(path, 'w', 'utf-8') as f:
        json.dump(jsonData, f, indent=4, ensure_ascii=False)

def cutButton(button):
    copyButton()
    button.menu.deleteLater()
    button.setParent(None)
    button.deleteLater()

def pasteButton(button, path=None):
    oldButtonData = getGIFButtonData(button)
    path = path + 'shelf_copy.json'
    # 在 Python 2.7 中，open 函数不支持 encoding 参数。你需要使用 codecs 模块来处理文件的编码。
    with codecs.open(path, 'r', 'utf-8') as f:
        jsonData = json.load(f)
    newButtonData = jsonData['shelfData']
    if newButtonData is None:
        return
    elif newButtonData == oldButtonData:
        return
    else:
        button.labelText = newButtonData['label']
        button.annotation = newButtonData['annotation']
        button.iconPath = newButtonData['image']
        button.command = newButtonData['command']
        button.size = newButtonData['size']

        button.menu.clear()
        button.addDefaultMenuItems()
        for key, value in newButtonData['menuItem'].items():
            if value == 'separator':
                button.menu.addSeparator()
            else:
                button.addMenuItem(label=value['label'], command=value['command'], icon=value['image'], annotation=value['annotation'])
        #update()

def deleteButton(button, path=None):
    if not os.path.exists(path):
        os.makedirs(path)

    shelf_recycle = path + 'shelf_recycle.json'
    if not os.path.exists(shelf_recycle):
        with codecs.open(shelf_recycle, 'w', 'utf-8') as f:
            json.dump({"shelfName": "buttonRecycle", "shelfData": {}}, f, ensure_ascii=False)

    buttonData = getGIFButtonData(button)

    with codecs.open(shelf_recycle, 'r', 'utf-8') as f:
        jsonData = json.load(f)
    shelfData = jsonData['shelfData']

    # buttonData 和 shelfData[key] 是一样的数据的话，删除这个数据
    # 对比每个buttonData[key] 和 shelfData[key][key] 的数据是否一样
    for i in list(shelfData.keys()):
        for key in buttonData.keys():
            if key == 'menuItem':
                for menuKey in buttonData[key].keys():
                    for iMenuKey in shelfData[i][key].keys():
                        if menuKey == iMenuKey:
                            if buttonData[key][menuKey] != shelfData[i][key][menuKey]:
                                #print(i,key,menuKey,iMenuKey,' :数据不一样')
                                break
            else:
                if buttonData[key] != shelfData[i][key]:
                    #print(i,key,' :数据不一样')
                    break
        else:
            #print(i,'数据一样')
            # print('数据一样')
            # 去掉这个数据，并重新排序
            shelfData.pop(i)
            shelfData = dict(sorted(shelfData.items(), key=lambda x: x[0]))
            jsonData['shelfData'] = shelfData

                
    # shelfData的 key 是 0 1 2 3 4 ...
    # 如果回收站数据大于等于20个，则删除第一个数据，jsonData[0] buttonData 插到最前 jsonData[0] = buttonData
    # 添加到最前面
    # 先将所有key+1
    for key in list(shelfData.keys()):
        shelfData[int(key)+1] = shelfData.pop(key)
    # 插入到第一个
    shelfData[0] = buttonData
    # 根据key排序
    shelfData = dict(sorted(shelfData.items(), key=lambda x: x[0]))
    # 超过20个数据，删除最后一个
    if len(shelfData) > 20:
        shelfData.popitem()

    jsonData['shelfData'] = shelfData
    with codecs.open(shelf_recycle, 'w', encoding='utf-8') as f:
        json.dump(jsonData, f, indent=4, ensure_ascii=False)

    # 删除按钮
    button.menu.deleteLater()
    button.setParent(None)
    button.deleteLater()  