# OneButtonManager

- This is a Python script project for managing custom gif buttons in Maya:
  - Initialize shelf layout
  - Add buttons and separators
  - Convert existing shelves
  - Save and load shelf data

## File List

- `GIFButton.py`: Script for creating and managing Maya shelf buttons, supporting GIF icon playback and pause
- `ShelfButtonManager.py`: An example of adding gif icons to the shelf

## Installation

- Drag and drop `install.mel` into the Maya window, and a dynamic siri button will be added to the toolbar
  - Click the button to add a new button to the toolbar
  - Double-click the button to add a separator
  - Right-click the button to edit the button and toolbar:
    - Convert existing shelves
    - Save and load shelf data
    - Edit button icons, styles, commands, menu items, etc.
    - Add, move, and delete menu items

## Usage

1. **Initialize shelf layout**:

   ```python
   shelf_button_manager = ShelfButtonManager()
   ```

2. **Add button**:

   ```python
   shelf_button_manager.addButton(
       icon="siri.gif",
       command='print("siri")',
       ctrlCommand='print("Ctrl Clicked!")'
   )
   shelf_button_manager.gifButton.addmenuItem(
       label=u"Custom Menu Item",
       command=u'warning(u"Custom Menu Item")',
       icon="white/Custom.png",
       annotation=u"This is a custom menu item"
   )
   shelf_button_manager.gifButton.addDefaultMenuItems()
   ```

3. **Add separator**:

   ```python
   shelf_button_manager.addSeparator()
   ```

4. **Save shelf data**:

   ```python
   shelf_button_manager.saveGifShelf()
   ```

5. **Load shelf data**:

   ```python
   shelf_button_manager.loadGifShelf()
   ```

## Example

- Here is a complete example that creates several sample icons in a custom toolbar, demonstrating how to use these features:

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
        label=u"Custom Menu Item",
        command=u'warning(u"Custom Menu Item")',
        icon="white/Custom.png",
        annotation=u"This is a custom menu item"
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

## Dependencies

- Maya2020+
- PySide2 or PySide6
- pymel
