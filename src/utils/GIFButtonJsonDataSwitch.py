# -*- coding: utf-8 -*-
def GIFButtonJsonDataSwitch(data):
    newDict = {}
    newDict['size'] = data['size']
    newDict['labelText'] = data['label']
    newDict['annotation'] = data['annotation']
    newDict['image'] = data['image']
    newDict['command'] = {
        'click': [data['sourceType'], data['command']],
        'doubleClick': [data['sourceType'], data['doubleClick']],
        'ctrlClick': ['python', data['ctrlClick']],
        'shiftClick': ['python', data['shiftClick']],
        'altClick': ['python', data['altClick']],
        'ctrlShiftClick': ['python', data['ctrlShiftClick']],
        'ctrlAltClick': ['python', data['ctrlAltClick']],
        'shiftAltClick': ['python', data['shiftAltClick']],
        'ctrlShiftAltClick': ['python', data['ctrlShiftAltClick']],
        'drag': ['python', data['drag']],
        'ctrlDrag': ['python', data['ctrlDrag']],
        'shiftDrag': ['python', data['shiftDrag']],
        'altDrag': ['python', data['altDrag']],
        'menuShowCommand': ['python', data['menuShowCommand']]
    }
    newDict['menuItem'] = {}
    for item in data['menuItem'].items():
        newDict['menuItem'][item]['label'] = data['menuItem'][item]['label']
        newDict['menuItem'][item]['annotation'] = data['menuItem'][item]['annotation']
        newDict['menuItem'][item]['image'] = data['menuItem'][item]['image']
        newDict['menuItem'][item]['command'] = {
            'click': [data['menuItem'][item]['sourceType'], data['menuItem'][item]['command']]
        }
    return newDict