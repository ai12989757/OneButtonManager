# OneButtonManager

- This is a Python script project for managing custom gif buttons in Maya:
  - Initialize shelf layout
  - Add buttons and separators
  - Convert existing shelves
  - Save and load shelf data

## File List

- `GIFButton.py`: Script for creating and managing Maya GIF buttons, supporting GIF icon playback and pause
- `ShelfButtonManager.py`: An example of adding gif icons to the shelf

## Environment

- Maya2017+
  - Tested with 2020, 2022, 2025

## Installation

- Drag and drop `install.mel` into the Maya window, and a prompt will indicate successful installation

## Usage

### Toolbar Management

- Right-click the menu bar
  - Add Button
    - Add a default button with no functionality
  - Add Separator
    - Add a default separator
  - Paste Button
    - Paste the button from the clipboard
  - Recycle Bin
    - Deleted buttons will be placed in the recycle bin and can be restored, up to 20 buttons
  - Convert Toolbar
    - Convert the existing toolbar to a new toolbar, retaining the original functionality
    - Icons on the new toolbar will be replaced with GIFButton
      - Right-click the icon to edit the button
  - Save Toolbar
    - Save the current toolbar information to a file /Documents/OneTools/data/shelf_xxxx.json
  - Import Toolbar
    - Import from files saved by OneButtonManager
  - Auto Load Toolbar
    - Automatically load all toolbars that meet the rules in the `/Documents/OneTools/data/` folder when Maya starts
  - Auto Save Toolbar
    - Automatically save the toolbar to `/Documents/OneTools/data/` when Maya closes
  - Language Switch
    - Switch between Chinese and English

### Button Editing

- Right-click the button
  - Edit
    - Edit
      - Open the button editing window
    - Copy
      - Copy the button to the clipboard
    - Cut
      - Cut the button to the clipboard
    - Paste
      - Paste the button from the clipboard to the current button
  - Delete
    - Delete the button
      - Deleted buttons will be placed in the recycle bin and can be restored, up to 20 buttons

### Button Editor

- Change Icon
- Change Command
- Change Tooltip
- Change Menu
  - Add Menu Item
  - Edit Menu Item
    - Modify Menu Name
    - Modify Menu Command
    - Modify Menu Icon
    - Modify Menu Tooltip
  - Delete Menu Item