# -*- coding: utf-8 -*-
import hashlib

def sl(text, language=0):
    outText = text
    language_dict = languageCheckDict()
    if language == 0:
        outText = text
    elif language == 1:
        if get_hashed_string(text) in language_dict:
            outText = language_dict[get_hashed_string(text)][0]
    return outText
        
# 创建一个中英文对照表
def languageCheckDict():
    # key: Chinese, value: [English, ...]
    language_dict = {
        get_hashed_string(u'简体中文'): ['English'],
        get_hashed_string(u'语言'): ['Language'],
        get_hashed_string(u"添加按钮"): ["Add Button"],
        get_hashed_string(u"点击添加一个新按钮"): ["Click to add a new button"],
        get_hashed_string(u"添加分隔符"): ["Add Separator"],
        get_hashed_string(u"点击添加一个新分隔符"): ["Click to add a new separator"],
        get_hashed_string(u"粘贴按钮"): ["Paste Button"],
        get_hashed_string(u"点击粘贴按钮"): ["Click to paste button"],
        get_hashed_string(u"回收站"): ["Recycle Bin"],
        get_hashed_string(u"删除的按钮保存在此处, 最多存放 20 个删除的按钮"): ["Deleted buttons are stored here, up to 20 deleted buttons can be stored"],
        get_hashed_string(u"清空回收站"): ["Empty Recycle Bin"],
        get_hashed_string(u"还原"): ["Restore"],
        get_hashed_string(u"将此按钮重新添加到当前工具栏"): ["Re-add this button to the current toolba"],
        get_hashed_string(u"删除"): ["Delete"],
        get_hashed_string(u"从回收站彻底删除此按钮, 注意: 不可恢复"): ["Permanently delete this button from the recycle bin. Note: Cannot be restored"],
        get_hashed_string(u"转换工具栏"): ["Convert Shelf"],
        get_hashed_string(u"点击转换当前工具栏"): ["Click to convert shelf to GIFShelf"], 
        get_hashed_string(u"还原工具栏"): ["Restore Shelf"],
        get_hashed_string(u"点击还原当前工具栏"): ["Click to restore GIFShelf"],
        get_hashed_string(u"保存工具栏"): ["Save Shelf"],
        get_hashed_string(u"点击保存当前工具栏"): ["Click to save GIFShelf"],
        get_hashed_string(u"导入工具栏"): ["Import Shelf"],
        get_hashed_string(u"点击导入工具栏"): ["Click to import GIFShelf"],
        get_hashed_string(u"自动加载工具栏"): ["Auto Load GIFShelf"],
        get_hashed_string(u"maya启动时自动加载data文件下的工具栏"): ["Auto load GIFShelf when Maya starts"],
        get_hashed_string(u"自动保存工具栏"): ["Auto Save GIFShelf"],
        get_hashed_string(u"maya关闭时自动保存当前工具栏"): ["Auto save GIFShelf when Maya closes"],
        get_hashed_string(u"编辑"): ["Edit"],
        get_hashed_string(u"点击打开编辑窗口"): ["Click to open the edit window"],
        get_hashed_string(u"复制"): ["Copy"],
        get_hashed_string(u"复制按钮"): ["Copy Button"],
        get_hashed_string(u"剪切"): ["Cut"],
        get_hashed_string(u"剪切按钮"): ["Cut Button"],
        get_hashed_string(u"粘贴"): ["Paste"],
        get_hashed_string(u"粘贴按钮"): ["Paste Button"],
        get_hashed_string(u"删除按钮"): ["Delete Button"],
        get_hashed_string(u"OneButton编辑器"): ["OneButton Editor"],
        get_hashed_string(u"名称:"): ["Name:"],
        get_hashed_string(u"路径:"): ["Path:"],
        get_hashed_string(u"动画:"): ["Animation:"],
        get_hashed_string(u"循环播放"): ["Loop"],
        get_hashed_string(u"离开停止"): ["Stop"],
        get_hashed_string(u"离开暂停"): ["Pause"],
        get_hashed_string(u"提示:"): ["Tip:"],
        get_hashed_string(u"点击命令"): ["Click Command"],
        get_hashed_string(u'点击命令'): ['Click Command'],
        get_hashed_string(u'双击命令'): ['Double Click Command'],
        get_hashed_string(u'Ctrl单击'): ['Ctrl Click'],
        get_hashed_string(u'Alt单击'): ['Alt Click'],
        get_hashed_string(u'Shift单击'): ['Shift Click'],
        get_hashed_string(u'Ctrl+Alt单击'): ['Ctrl+Alt Click'],
        get_hashed_string(u'Ctrl+Shift单击'): ['Ctrl+Shift Click'],
        get_hashed_string(u'Alt+Shift单击'): ['Alt+Shift Click'],
        get_hashed_string(u'Ctrl+Alt+Shift单击'): ['Ctrl+Alt+Shift Click'],
        get_hashed_string(u'左击拖动'): ['Left Drag'],
        get_hashed_string(u'Ctrl左击拖动'): ['Ctrl Left Drag'],
        get_hashed_string(u'Alt左击拖动'): ['Alt Left Drag'],
        get_hashed_string(u'Shift左击拖动'): ['Shift Left Drag'],
        get_hashed_string(u'右击菜单'): ['Right Click Menu'],
        get_hashed_string(u'双击更改图标'): ['Double click to change icon'],
        get_hashed_string(u'双击更改名称'): ['Double click to change name'],
        get_hashed_string(u'语言:'): ['Language:'],
        get_hashed_string(u'请输入菜单提示'): ['Please enter menu tip'],
        get_hashed_string(u'菜单显示时执行的命令'): ['Command executed when menu is shown'],
        get_hashed_string(u'应用'): ['Apply'],
        get_hashed_string(u'应用并关闭'): ['Apply and Close'],
        get_hashed_string(u'关闭'): ['Close'],
        get_hashed_string(u'当菜单弹出前执行命令，一般用于更新菜单项'): ['Execute command before menu pops up, generally used to update menu items'],
        get_hashed_string(u'请输入命令'): ['Please enter command'],
        get_hashed_string(u"请输入命令\n使用 print(self.value) 获取可调用的值\n例子: \n# 沿x轴移动当前选中对象，移动距离为拖动值*0.1\nmove(self.valueX*0.1,0,0)"): ["Please enter command\nUse print(self.value) to get callable values\nExample: \n# Move the currently selected object along the x-axis, the distance moved is the drag value*0.1\nmove(self.valueX*0.1,0,0)"],
        get_hashed_string(u'选择图标'): ['Select Icon'],
        get_hashed_string(u"图标文件 (*.PNG *.BMP *.GIF *.JPEG *.JPG *.SVG *.ICO)"): ["Icon Files (*.PNG *.BMP *.GIF *.JPEG *.JPG *.SVG *.ICO)"],
    }
    return language_dict

# 定义一个函数，根据输入的字符串，返回一个固定的哈希值字符串
def get_hashed_string(input_string):
    # 使用 SHA-256 哈希函数
    hash_object = hashlib.sha256(input_string.encode('utf-8'))
    # 获取哈希值的十六进制表示
    hex_dig = hash_object.hexdigest()
    return hex_dig