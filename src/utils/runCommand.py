# -*- coding: utf-8 -*-
from maya import mel
import maya.cmds as cmds


# 兼容 Python 2 和 3 的 exec 函数
def exec_(code, globals=None, locals=None):
    if globals is None:
        globals = {}
    globals.update({
        '__builtins__': __builtins__,
    })
    exec(code, globals, locals)

def runCommand(widget, command, trigger='click'):
    
    if widget.type == 'QWidget':
    #if hasattr(widget, 'mouseState'):
        # if widget.mouseState in ['leftPress','leftRelease'] and trigger not in ['leftPress','leftRelease']:
        #     if widget.mouseState == 'leftPress':
        #         cmds.undoInfo(openChunk=True)
        #     if widget.mouseState == 'leftRelease':
        #         cmds.undoInfo(closeChunk=True)
        # else:
        if not command: return
        if trigger not in command: return
        if trigger not in command.keys(): return
        if widget.type == 'QWidget':
            #print(command[trigger][1])
            
            if command[trigger][1] == '' or command[trigger][1] is None: return
            if command[trigger][0] == 'python': 
                cmds.evalDeferred(lambda: exec_(command[trigger][1], widget.context))
            elif command[trigger][0] == 'mel':
                commendText = repr(command[trigger][1])
                commendText = "mel.eval(" + commendText + ")"
                if trigger in ['drag', 'ctrlDrag', 'shiftDrag', 'altDrag', 'ctrlShiftDrag', 'ctrlAltDrag', 'altShiftDrag', 'ctrlAltShiftDrag']:
                    mel.eval("string $mouseState=\""+str(widget.mouseState)+"\";")
                    mel.eval("int $deltaX="+str(widget.delta.x())+";")
                    mel.eval("int $deltaY="+str(widget.delta.y())+";")
                exec_(commendText)
            elif command[trigger][0] == 'function': 
                command[trigger][1]()
    elif widget.type == 'QAction':
        if not command: return
        if trigger not in command: return
        if trigger not in command.keys(): return
        if command[trigger][1] == '' or command[trigger][1] is None: return
        if command[trigger][0] == 'python': 
            cmds.undoInfo(openChunk=True)
            cmds.evalDeferred(lambda: exec_(command[trigger][1], widget.context))
            cmds.undoInfo(closeChunk=True)
        elif command[trigger][0] == 'mel':
            commendText = repr(command[trigger][1])
            commendText = "mel.eval(" + commendText + ")"
            cmds.undoInfo(openChunk=True)
            exec_(commendText)
            cmds.undoInfo(closeChunk=True)
        elif command[trigger][0] == 'function': 
            cmds.undoInfo(openChunk=True)
            command[trigger][1]()
            cmds.undoInfo(closeChunk=True)