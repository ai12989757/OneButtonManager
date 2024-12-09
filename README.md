# OneButtonManager

- 这是一个用于管理Maya自定义gif按钮的Python脚本项目：
  - 初始化工具架布局
  - 添加按钮和分隔符
  - 转化现有工具架
  - 保存和加载工具架数据

## 文件列表

- `GIFButton.py`: 创建和管理Maya工具架按钮的脚本，支持GIF图标的播放和暂停
- `ShelfButtonManager.py`: 一个示例，在工具架上添加gif图标

## 安装方法

- 将`install.mel`拖放到Maya窗口中，工具栏上会添加一个动态的siri按钮
  - 点击按钮添加一个新的按钮到工具栏上
  - 双击按钮添加一个分隔符
  - 右键按钮编辑按钮和工具栏、
    - 可以转化现有工具栏
    - 可以保存和加载工具栏数据
    - 编辑按钮图标、样式、命令、菜单项等
    - 添加、移动、删除菜单项

## 使用方法

1. **初始化工具架布局**:

   ```python
   shelf_button_manager = ShelfButtonManager()
   ```

2. **添加按钮**:

   ```python
   shelf_button_manager.addButton(
       icon="siri.gif",
       command='print("siri")',
       ctrlCommand='print("Ctrl Clicked!")'
   )
   shelf_button_manager.gifButton.addmenuItem(
       label=u"自定义菜单项",
       command=u'warning(u"自定义菜单项")',
       icon="white/Custom.png",
       annotation=u"这是一个自定义菜单项"
   )
   shelf_button_manager.gifButton.addDefaultMenuItems()
   ```

3. **添加分隔符**:

   ```python
   shelf_button_manager.addSeparator()
   ```

4. **保存工具架数据**:

   ```python
   shelf_button_manager.saveGifShelf()
   ```

5. **加载工具架数据**:

   ```python
   shelf_button_manager.loadGifShelf()
   ```

## 示例

- 以下是一个完整的示例，运行后在自定义工具栏里创建几个示例图标，展示了如何使用这些功能：

```python
def main():
    sys.dont_write_bytecode = True
    
    gShelfTopLevel = mel.eval('$temp=$gShelfTopLevel')
    if 'Custom' in tabLayout(gShelfTopLevel, q=True, ca=True):
        deleteUI('Custom', lay=True)
    mel.eval('addNewShelfTab("Custom")')
    
    if "Custom" not in shelfTabLayout(gShelfTopLevel, q=True, ca=True):
        mel.eval('addNewShelfTab("Custom")')
    else:
        shelfTabLayout(gShelfTopLevel, edit=True, selectTab="Custom")

    shelf_button_manager = ShelfButtonManager()
    
    shelf_button_manager.addButton(
        icon="siri.gif",
        command='print("siri")',
        ctrlCommand='print("Ctrl Clicked!")'
    )
    shelf_button_manager.gifButton.addDefaultMenuItems()

    shelf_button_manager.addSeparator()

    shelf_button_manager.addButton(
        icon="cat4.gif",
        command='print("cat4")',
        ctrlCommand='print("Ctrl Clicked!")'
    )
    shelf_button_manager.gifButton.addDefaultMenuItems()

    shelf_button_manager.addButton(icon="cat3.gif",command='print("cat3")')
    shelf_button_manager.gifButton.addMenuItem(
        label=u"自定义菜单项",
        command=u'warning(u"自定义菜单项")',
        icon="white/Custom.png",
        annotation=u"这是一个自定义菜单项"
    )
    shelf_button_manager.gifButton.menu.addSeparator()
    shelf_button_manager.gifButton.addDefaultMenuItems()

    shelf_button_manager.addButton(
        icon="cat2.gif",
        annotation=u'test',
        command='print("cat2")'
    )
    shelf_button_manager.gifButton.addDefaultMenuItems()

    shelf_button_manager.addButton(
        icon="cat1.gif",
        annotation=u'annotateInfo',
        command='print("cat1")'
    )
    shelf_button_manager.gifButton.addDefaultMenuItems()
```

## 依赖

- Maya2020+
- PySide2 或 PySide6
- pymel
