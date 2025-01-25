from maya import mel
import maya.cmds as cmds

def runCommand(widget, command, trigger='click'):
    if widget.type == 'QWidget':
    #if hasattr(widget, 'mouseState'):
        if widget.mouseState in ['leftPress','leftRelease']:
            if widget.mouseState == 'leftPress':
                cmds.undoInfo(openChunk=True)
            if widget.mouseState == 'leftRelease':
                cmds.undoInfo(closeChunk=True)
        else:
            if not command: return
            if trigger not in command: return
            if trigger not in command.keys(): return
            if widget.type == 'QWidget':
                if command[trigger][0] == 'python': 
                    cmds.evalDeferred(lambda: exec(command[trigger][1], widget.context))
                elif command[trigger][0] == 'mel':
                    commendText = repr(command[trigger][1])
                    commendText = "mel.eval(" + commendText + ")"
                    if trigger in ['drag', 'ctrlDrag', 'shiftDrag', 'altDrag', 'ctrlShiftDrag', 'ctrlAltDrag', 'altShiftDrag', 'ctrlAltShiftDrag']:
                        mel.eval("string $mouseState=\""+str(widget.mouseState)+"\";")
                        mel.eval("int $deltaX="+str(widget.delta.x())+";")
                        mel.eval("int $deltaY="+str(widget.delta.y())+";")
                    exec(commendText)
                elif command[trigger][0] == 'function': 
                    command[trigger][1]()
    elif widget.type == 'QAction':
        if not command: return
        if trigger not in command: return
        if trigger not in command.keys(): return
        if command[trigger][0] == 'python': 
            cmds.undoInfo(openChunk=True)
            cmds.evalDeferred(lambda: exec(command[trigger][1], widget.context))
            cmds.undoInfo(closeChunk=True)
        elif command[trigger][0] == 'mel':
            commendText = repr(command[trigger][1])
            commendText = "mel.eval(" + commendText + ")"
            cmds.undoInfo(openChunk=True)
            exec(commendText)
            cmds.undoInfo(closeChunk=True)
        elif command[trigger][0] == 'function': 
            cmds.undoInfo(openChunk=True)
            command[trigger][1]()
            cmds.undoInfo(closeChunk=True)