
from maya import mel

def returnShelfData(shelfFile):
    """
    Returns the shelf data from the shelf file.
    """
    shelfFile = shelfFile.replace('\\', '/')
    shelfType = ''
    if '.mel' in shelfFile:
        shelfType = 'mel'
    elif '.json' in shelfFile:
        shelfType = 'json'
    else:
        return mel.eval('warning -n "不支持的文件类型";')
    
    shelfName = shelfFile.split('.mel')[0].split('/')[-1].replace('shelf_', '')
    if shelfName not in mel.eval('shelfTabLayout -q -ca $gShelfTopLevel'):
        mel.eval('addNewShelfTab("'+shelfName+'")')
    if mel.eval('shelfLayout -q -ca '+shelfName) is not None:
        for i in mel.eval('shelfLayout -q -ca '+shelfName):
            mel.eval('deleteUI '+i)

    if shelfType == 'mel':
        returnMelShelfData(shelfFile, shelfName)
    elif shelfType == 'json':
        returnJsonShelfData(shelfFile, shelfName)

def returnMelShelfData(shelfFile, shelfName):

    mel.eval('setParent("'+shelfName+'")')
    mel.eval('source "'+shelfFile+'"')
    with open(shelfFile, 'r') as f:
        firstLine = f.readline()
    if 'global proc' not in firstLine:
        return mel.eval('warning -n "该shelf文件内容有误";')
    funcName = firstLine.split('global proc ')[1].split(' ')[0]
    try:
        mel.eval('%s()' % funcName)
        return mel.eval('print("// 结果: '+shelfName+' 还原成功")')
    except:
        return mel.eval('warning -n "该shelf文件内容有误";')
    
def returnJsonShelfData(shelfFile, shelfName):
    pass