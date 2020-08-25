"""
Script for cut of unimportant pats of logs to upload on the website
"""

import sys


LOOK_FOR = (
    'ENCOUNTER_START',
    'UNIT_DIED',
    'ENCOUNTER_END',
    'SPELL_AURA_APPLIED',
    'SPELL_CAST_START',
    'SPELL_AURA_REMOVED',
    'COMBATANT_INFO',

    'SPELL_CAST_SUCCESS',  # TODO remove with the old version
)
path = sys.argv[1]

if path[-1] == '"':
    new_path = path[:-1] + '_processed.log"'
else:
    new_path = path + '_processed.log'

first_row = True    

lines = []
with open(path, 'r', encoding='utf-8') as from_file, open(new_path, 'w', encoding='utf-8') as to_file:
    for line in from_file.readlines():
        if first_row:
            first_row = False
            lines.append(line)
            continue
 
        for substring in LOOK_FOR:
            if substring in line:
                lines.append(line)
                break
                
    to_file.writelines(lines)
