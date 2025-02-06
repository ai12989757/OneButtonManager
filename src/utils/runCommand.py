# -*- coding: utf-8 -*-
from maya import mel
import maya.cmds as cmds

def exec_command(command, context):
    exec(command, {}, context)

def exec_mel_command(command):
    exec(command)

def runCommand(widget, command, trigger='click'):
    if widget.type == 'QWidget':
        if not command: return
        if trigger not in command: return
        if trigger not in command.keys(): return
        if widget.type == 'QWidget':
            if command[trigger][1] == '' or command[trigger][1] is None: return
            if command[trigger][0] == 'python': 
                cmds.evalDeferred(lambda: exec_command(command[trigger][1], widget.context))
            elif command[trigger][0] == 'mel':
                commendText = repr(command[trigger][1])
                commendText = "mel.eval(" + commendText + ")"
                if trigger in ['drag', 'ctrlDrag', 'shiftDrag', 'altDrag', 'ctrlShiftDrag', 'ctrlAltDrag', 'altShiftDrag', 'ctrlAltShiftDrag']:
                    mel.eval("string $mouseState=\""+str(widget.mouseState)+"\";")
                    mel.eval("int $deltaX="+str(widget.delta.x())+";")
                    mel.eval("int $deltaY="+str(widget.delta.y())+";")
                exec_mel_command(commendText)
            elif command[trigger][0] == 'function': 
                command[trigger][1]()
    elif widget.type == 'QAction':
        if not command: return
        if trigger not in command: return
        if trigger not in command.keys(): return
        if command[trigger][1] == '' or command[trigger][1] is None: return
        if command[trigger][0] == 'python': 
            cmds.undoInfo(openChunk=True)
            cmds.evalDeferred(lambda: exec_command(command[trigger][1], widget.context))
            cmds.undoInfo(closeChunk=True)
        elif command[trigger][0] == 'mel':
            commendText = repr(command[trigger][1])
            commendText = "mel.eval(" + commendText + ")"
            cmds.undoInfo(openChunk=True)
            exec_mel_command(commendText)
            cmds.undoInfo(closeChunk=True)
        elif command[trigger][0] == 'function': 
            cmds.undoInfo(openChunk=True)
            command[trigger][1]()
            cmds.undoInfo(closeChunk=True)