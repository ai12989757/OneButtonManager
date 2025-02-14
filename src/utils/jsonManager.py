import os
import json
import codecs
from collections import OrderedDict

def read(file):
    if not file:
        return None
    if not os.path.exists(file):
        return None
    try:
        with codecs.open(file, 'r', 'utf-8') as f:
            return json.load(f)
    except:
        with open(file, 'r') as f:
            return json.load(f,object_pairs_hook=OrderedDict)
        
def write(file, data):
    if not file:
        return False
    try:
        with codecs.open(file, 'w', 'utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except:
        with open(file, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    finally:
        try:
            from maya import mel
            mel.eval(u'print "// 信息: %s"' % file)
        except:
            print('// Info: %s' % file)
