'''
Copies the target java file and all its dependencies recursively to another directory

ENTRY_POINT The first class to strart the extraction from
OUTPUT_DIR where all the files will be copied to
'''

import os
import glob
import shutil
import re

ROOT_DIR = '../'
ENTRY_POINT = './my_project/AwesomeJavaClass.java'
OUTPUT_DIR = './output/'

lookup = dict()

print('Populating LUT')
def lut_pop(expression):
    for filename in glob.iglob(ROOT_DIR + expression, recursive=True):
        with open(filename, encoding='utf-8') as f:
            try:
                lines = f.readlines()
                find_package = filter(lambda line: line.startswith('package'), lines)
                package_id = list(find_package)[0].split(' ')[1].split(';')[0]
                class_name = filename.split('/')[-1].split('.')[0]
                package_id += '.' + class_name
            except Exception as e:
                print(filename, e)
            
        lookup[package_id] = filename

lut_pop('**/*.java')

imports_to_traverse = set()
imports_traversed = set()

# Imports that were not found in the look up table
lut_misses = set()

def get_all_imports(lines):
    filter_op = filter(lambda line: line.startswith('import '), lines)
    map_op = map(lambda line: line.replace(' static ',' ').split(' ')[1].split(';')[0], filter_op)
    return set(map_op)

def get_lines_from_file(filename):
    with open(filename, encoding='utf-8') as f:
        lines = f.read().split('\n')
    return lines

print('Traversing')
lines = get_lines_from_file(ENTRY_POINT)
package_names = get_all_imports(lines)
imports_to_traverse.update(package_names)

while len(imports_to_traverse) > 0:
    package_name = imports_to_traverse.pop()

    # Check for broken imports
    if package_name not in lookup:
        keys = lookup.keys()

        # If nested class
        uncascaded = list(filter(lambda x: package_name.startswith(x),keys))
        if len(uncascaded) == 0:
            # If broken import, then skip
            lut_misses.add(package_name)
            continue
        lookup[package_name] = lookup[uncascaded[0]]

    # If file is already traversed then skip
    if package_name in imports_traversed:
        continue

    # Extract all packages to import
    file_name = lookup[package_name]
    lines = get_lines_from_file(file_name)
    package_names = get_all_imports(lines)

    imports_to_traverse.update(package_names)

    imports_traversed.add(package_name)

# Drop all the java imports because they come with JDK
lut_misses = list(filter(lambda x : not x.startswith('java'), lut_misses))

def get_output_file_name(file_name):
    with open(file_name, encoding='utf-8') as f:
        lines = f.readlines()
        line = list(filter(lambda x:x.startswith('package'),lines))[0]
        # Lets say that the java class belongs to org.company.subpackage
        # Then it will be put in  OUTPUT_DIR/org/company/subpackage/ClassName.java
        return OUTPUT_DIR + re.findall('package (.*);', line)[0].replace('.','/')

def cpy(input_file_name):
    output_file_name = get_output_file_name(input_file_name)
    os.makedirs(output_file_name, exist_ok=True)    
    shutil.copy(input_file_name, output_file_name)

print('Copying')
input_file_names = [ENTRY_POINT]
for package in imports_traversed:
    input_file_names.append(lookup[package])

for input_file_name in input_file_names:
    path = '/'.join(input_file_name.split('/')[:-1])
    # Java classes in the same package do not need to be imported
    # So, copy all the java files in that package
    for file_name in os.listdir(path):
        if not file_name.endswith('.java'):
            continue
        cpy(os.path.join(path , file_name))
