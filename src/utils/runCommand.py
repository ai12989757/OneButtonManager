# -*- coding: utf-8 -*-
from maya import mel
import maya.cmds as cmds

widget_instance = None

def exec_mel_command(command):
    exec(command)

def runCommand(widget, command, trigger='click'):
    global widget_instance
    widget_instance = widget
    if widget.type == 'QWidget':
        if not command: return
        if trigger not in command: return
        if trigger not in command.keys(): return
        if widget.type == 'QWidget':
            if command[trigger][1] == '' or command[trigger][1] is None: return
            if command[trigger][0] == 'python': 
                def runPythonCommand(command):
                    global widget_instance
                    exec("self = widget_instance", globals())
                    exec(command, globals())
                try:
                    cmds.undoInfo(openChunk=True)
                    runPythonCommand(command[trigger][1])
                    cmds.undoInfo(closeChunk=True)
                except Exception as e:
                    cmds.undoInfo(closeChunk=True)
                    # 打印错误信息
                    mel.eval('print("// 错误: '+str(e)+' //\\n")')

            elif command[trigger][0] == 'mel':
                commendText = repr(command[trigger][1])
                commendText = "mel.eval(" + commendText + ")"
                if trigger in ['drag', 'ctrlDrag', 'shiftDrag', 'altDrag', 'ctrlShiftDrag', 'ctrlAltDrag', 'altShiftDrag', 'ctrlAltShiftDrag']:
                    mel.eval("string $mouseState=\""+str(widget.mouseState)+"\";")
                    mel.eval("int $deltaX="+str(widget.delta.x())+";")
                    mel.eval("int $deltaY="+str(widget.delta.y())+";")
                try:
                    cmds.undoInfo(openChunk=True)
                    exec_mel_command(commendText)
                    cmds.undoInfo(closeChunk=True)  
                except Exception as e:
                    pass
            elif command[trigger][0] == 'function': 
                try:
                    cmds.undoInfo(openChunk=True)
                    command[trigger][1]()
                    cmds.undoInfo(closeChunk=True)  
                except Exception as e:
                    cmds.undoInfo(closeChunk=True)
                    mel.eval('print("// 错误: '+str(e)+' //\\n")')
                    
    elif widget.type == 'QAction':
        if not command: return
        if trigger not in command: return
        if trigger not in command.keys(): return
        if command[trigger][1] == '' or command[trigger][1] is None: return
        if command[trigger][0] == 'python': 
            def runPythonCommand(command):
                global widget_instance
                exec("self = widget_instance", globals())
                exec(command, globals())
            try:
                cmds.undoInfo(openChunk=True)
                runPythonCommand(command[trigger][1])
                cmds.undoInfo(closeChunk=True)
            except Exception as e:
                cmds.undoInfo(closeChunk=True)
                mel.eval('print("// 错误: '+str(e)+' //\\n")')
        elif command[trigger][0] == 'mel':
            commendText = repr(command[trigger][1])
            commendText = "mel.eval(" + commendText + ")"
            try:
                cmds.undoInfo(openChunk=True)
                exec_mel_command(commendText)
                cmds.undoInfo(closeChunk=True)
            except Exception as e:
                pass
        elif command[trigger][0] == 'function': 
            try:
                cmds.undoInfo(openChunk=True)
                command[trigger][1]()
                cmds.undoInfo(closeChunk=True)  
            except Exception as e:
                cmds.undoInfo(closeChunk=True)
                mel.eval('print("// 错误: '+str(e)+' //\\n")')