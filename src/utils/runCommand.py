# -*- coding: utf-8 -*-
from maya import mel, cmds

widget_instance = None
class RunCommand:
    def __init__(self, widget,command,trigger='click'):
        self.widget = widget
        self.command = command
        self.trigger = trigger

    def ckeckCommand(self):
        if not self.command: return False
        if self.trigger not in self.command: return False
        if self.trigger not in self.command.keys(): return False
        if self.command[self.trigger][1] == '' or self.command[self.trigger][1] is None: return False
        return True

    def runPythonCommand(self, command):
        global widget_instance
        widget_instance = self.widget
        exec("self = widget_instance", globals())
        exec(command, globals())

    def leftPR(self):
        '''
        用于处理 'leftPress', 'leftRelease' 触发的命令
        不开启撤销块
        '''
        if self.trigger not in ['leftPress', 'leftRelease']: return
        cmds.undoInfo(openChunk=True, infinity=True, chunkName='OneToolsRunCommand_leftPR')
        try:
            if self.trigger not in ['leftPress', 'leftRelease']: return
            if self.command[self.trigger][0] == 'python': 
                self.runPythonCommand(self.command[self.trigger][1])
            elif self.command[self.trigger][0] == 'mel':
                commendText = repr(self.command[self.trigger][1])
                commendText = "mel.eval(" + commendText + ")"
                exec(commendText)
            elif self.command[self.trigger][0] == 'function': 
                self.command[self.trigger][1]()
        except Exception as e:
            if self.command[self.trigger][0] == 'mel':
                pass
            else:
                mel.eval('print("// 错误: '+str(e)+' //\\n")')
        finally:
            cmds.undoInfo(closeChunk=True)

    def runCommand(self):
        '''
        用于处理 'click', 'doubleClick', 'middleClick', 'rightClick', 'ctrlClick', 'shiftClick', 'altClick', 'ctrlShiftClick', 'ctrlAltClick', 'altShiftClick', 'ctrlAltShiftClick' 触发的命令
        开启撤销块
        '''
        if not self.ckeckCommand(): return
        if self.trigger in ['leftPress', 'leftRelease']: return
        cmds.undoInfo(openChunk=True, infinity=True, chunkName='OneToolsRunCommand')
        try:
            if self.command[self.trigger][0] == 'python': 
                self.runPythonCommand(self.command[self.trigger][1])
            elif self.command[self.trigger][0] == 'mel':
                commendText = repr(self.command[self.trigger][1])
                commendText = "mel.eval(" + commendText + ")"
                exec(commendText)
            elif self.command[self.trigger][0] == 'function': 
                self.command[self.trigger][1]()
        except Exception as e:
            if self.command[self.trigger][0] == 'mel':
                pass
            else:
                mel.eval('print("// 错误: '+str(e)+' //\\n")')
        finally:
            cmds.undoInfo(closeChunk=True)

    def runDragCommand(self):
        '''
        用于处理 'drag', 'ctrlDrag', 'shiftDrag', 'altDrag', 'ctrlShiftDrag', 'ctrlAltDrag', 'altShiftDrag', 'ctrlAltShiftDrag' 触发的命令
        不开启撤销块
        添加mel变量
        '''
        if not self.ckeckCommand(): return
        if self.trigger not in ['drag', 'ctrlDrag', 'shiftDrag', 'altDrag', 'ctrlShiftDrag', 'ctrlAltDrag', 'altShiftDrag', 'ctrlAltShiftDrag']:
            return
        try:
            if self.command[self.trigger][0] == 'python': 
                self.runPythonCommand(self.command[self.trigger][1])
            elif self.command[self.trigger][0] == 'mel':
                commendText = repr(self.command[self.trigger][1])
                commendText = "mel.eval(" + commendText + ")"
                mel.eval("string $mouseState=\""+str(self.widget.mouseState)+"\";")
                mel.eval("int $deltaX="+str(self.widget.delta.x())+";")
                mel.eval("int $deltaY="+str(self.widget.delta.y())+";")
                exec(commendText)
            elif self.command[self.trigger][0] == 'function': 
                self.command[self.trigger][1]()
        except Exception as e:
            if self.command[self.trigger][0] == 'mel':
                pass
            else:
                mel.eval('print("// 错误: '+str(e)+' //\\n")')