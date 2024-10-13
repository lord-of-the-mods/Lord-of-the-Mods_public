from datetime import datetime
import os
import shutil

from file_interpreter import load_items, load_items_part, print_items, print_items_part, comment_out, recognize_item_class
from constants import INI_PATH_PART, INI_COMMENTS, INI_PARAMETERS, LEVEL_INDENT, LOG_PATH, InternalError
from settings import current, MODULES_LIBRARY

# TODO later: reference checker
# TODO later: automated proposition of #include creation or child adopting


def log(output):
    if os.path.isfile(f'{LOG_PATH}/file_changes.txt'):
        with open(f'{LOG_PATH}/file_changes.txt', 'a') as log_file:
            log_file.write(output + '\n')
    else:
        with open(f'{LOG_PATH}/file_changes.txt', 'w') as log_file:
            log_file.write(output + '\n')


def convert_string(string, direction='automatic'):
    """
    converts the \n \t \r characters for reading or for finding the string in a file
    :param string: str to convert
    :param direction: 'automatic', 'process', 'display'
    :return: converted string
    """
    to_convert = {
        '\n': '\\n',
        '\t': '\\t',
        '\r': '\\r',
        ' ': '·'
    }
    for key in to_convert:
        if direction == 'process' or to_convert[key] in string and direction != 'display':
            for character in to_convert:
                string = string.replace(to_convert[character], character)
            return string
        elif key in string or direction == 'display':
            for character in to_convert:
                string = string.replace(character, to_convert[character])
            return string
        else:
            return string


# def find_text(find, in_file_or_folder, exception='', mode=0):
#     """
#      finds a given string in a given file or folder of files.
#     :param find:
#     :param in_file_or_folder:
#     :param exception:
#     :param mode: mode 2 returns the first line where the string was found. It returns an empty string if not found
#     :return:
#     """
#     output = ''
#     if not find:
#         return 'file_editor.find_text() aborted - empty string to find'
#     # if current(MODULES_LIBRARY) not in in_file_or_folder.replace('\\', '/'):
#     #     return 'file_editor.replace_text() aborted - item not in MODS_FOLDER'
#     if mode == 0:
#         output += f' command: find "{convert_string(find, direction="display")}"\n\tin {in_file_or_folder}.\nresult:'
#     find = convert_string(find, direction='process')
#     if in_file_or_folder in exception:
#         return output
#     if os.path.isdir(in_file_or_folder):
#         file_paths = os.listdir(in_file_or_folder)
#         for file_path in file_paths:
#             output += find_text(find, f'{in_file_or_folder}/{file_path}', mode=1)
#     elif os.path.isfile(in_file_or_folder):
#         try:
#             # with open(in_file_or_folder, 'r') as file:
#             #     file_content = file.read()
#             file_content = print_items(file=in_file_or_folder)
#             if file_content.count(find) > 0:
#                 if mode < 2:
#                     output += f'\tin {in_file_or_folder} found {file_content.count(find)}:\n'
#                     file_content_split = file_content.split(find)
#                     index_line = 1
#                     for content_part in file_content_split[:-1]:
#                         index_line += content_part.count('\n')
#                         text_line = file_content.split('\n')[index_line - 1]
#                         output += f'\t\tin line {index_line} "{text_line}"\n'
#                 else:
#                     output = file_content[file_content.rfind('#include', 0, file_content.find(find)):
#                                           file_content.find('\n', file_content.find(find))]
#                     # output = in_file_or_folder
#             elif mode == 0:
#                 output += f'\tfound none\n'  # {file_content.count(find)}
#         except UnicodeDecodeError:
#             output += f'file_editor.find_text() error: file {in_file_or_folder} unreadable'
#         except ValueError:
#             output += f'file_editor.find_text() error: ValueError'
#     return output


# def replace_text(find, replace_with=None, in_file_or_folder='', exception='', mode=0):
#     """ replaces a given string by another in a given file or folder of files """
#     output = ''
#     if not find:
#         return 'file_editor.replace_text() aborted - empty string to find'
#     # if current(MODULES_LIBRARY) not in in_file_or_folder.replace('\\', '/'):
#     #     return 'file_editor.replace_text() aborted - item not in MODS_FOLDER'
#     if mode == 0:
#         output += f'{datetime.now()}'
#         output += f' command: replace "{convert_string(find, direction="display")}"\n'
#         output += f'\twith "{replace_with}"\n\tin {in_file_or_folder}.\n'
#         if exception:
#             output += f'\texcept in "{exception}"'
#         output += 'result: '
#     find = convert_string(find, direction='process')
#     if ', ' in in_file_or_folder and mode == 0:
#         for scope_element in in_file_or_folder.split(', '):
#             output += replace_text(find, replace_with, scope_element, exception, mode=1)
#     if in_file_or_folder in exception:
#         return output
#     if os.path.isfile(in_file_or_folder):
#         try:
#             # with open(in_file_or_folder, 'r') as file:
#             #     file_content = file.read()
#             file_content = print_items(load_items(in_file_or_folder))[0]
#             if file_content.count(find) > 0:
#                 new_file_content = file_content.replace(find, replace_with)
#                 with open(in_file_or_folder, 'w') as file:
#                     file.write(new_file_content)
#                 output += f'\t{file_content.count(find)} replaced in {in_file_or_folder}\n'
#         except UnicodeDecodeError:
#             print(f'file_editor.replace_text() error: file {in_file_or_folder} unreadable')
#     elif os.path.isdir(in_file_or_folder):
#         file_paths = os.listdir(in_file_or_folder)
#         for file_path in file_paths:
#             output += replace_text(find, replace_with, f'{in_file_or_folder}/{file_path}', mode=1)  # mode=0
#         # if mode == 0:
#     log(output)
#     return output


def find_replace_text(find, replace_with=None, scope='', exceptions=None, mode='initiate'):
    """ replaces a given string by another in a given file or folder of files """
    output = ''
    if not find:
        return 'file_editor.replace_text() aborted - empty string to find'
    if 'initiate' in mode:
        output += f'{datetime.now()}'
        if replace_with is not None:
            output += f' command: replace "{convert_string(find, direction="display")}"\n'
            output += f'\twith "{convert_string(replace_with, direction="display")}"\n\tin {scope}.\n'
        else:
            output += f' command: find "{convert_string(find, direction="display")}"\n'
            output += f' in {scope}. \n'
        if exceptions:
            output += f'\texcept in {str(exceptions).strip("[]")}\n'
        output += 'result: '
    find = convert_string(find, direction='process')
    if replace_with is not None:
        replace_with = convert_string(replace_with, direction='process')
    if ', ' in scope and 'initiate' in mode:
        for scope_element in scope.split(', '):
            output += find_replace_text(find, replace_with, scope_element, exceptions, mode='part')
        return output
    if exceptions:
        if scope in exceptions:
            return output
    if os.path.isfile(scope):
        try:
            file_content = print_items(file=scope)
            if file_content.lower().count(find.lower()) > 0:
                if 'include' in mode:
                    output = file_content[
                             file_content.rfind('#include', 0, file_content.lower().find(find.lower())):
                             file_content.find('\n', file_content.lower().find(find.lower()))]
                elif replace_with is not None:
                    new_file_content = ''  # file_content.replace(find, replace_with)
                    output += f'\t{file_content.lower().count(find.lower())} replaced in {scope}\n'
                    index_line = 1
                    content_parts = file_content.lower().split(find.lower())
                    for content_part in content_parts:
                        index_line += content_part.count('\n')
                        text_line = file_content.split('\n')[index_line - 1]
                        if content_part != content_parts[-1]:
                            output += f'\t\tin line {index_line} "{text_line}"\n'
                        new_file_content += '\n'.join(file_content.split('\n')[:index_line - 1])
                        new_file_content += text_line.replace(find, replace_with)
                    with open(scope, 'w') as file:
                        file.write(new_file_content)
                else:
                    output += f'\tin {scope} found {file_content.lower().count(find.lower())}:\n'
                    index_line = 1
                    for content_part in file_content.lower().split(find.lower())[:-1]:
                        index_line += content_part.count('\n')
                        text_line = file_content.split('\n')[index_line - 1]
                        output += f'\t\tin line {index_line} "{text_line}"\n'
            elif 'initiate' in mode:
                output += f'\tfound none\n'
        except UnicodeDecodeError:
            print(f'file_editor.replace_text() error: file {scope} unreadable')
    elif os.path.isdir(scope):
        file_paths = os.listdir(scope)
        for file_path in file_paths:
            output += find_replace_text(find, replace_with, f'{scope}/{file_path}', exceptions, mode='part')  # mode=0
    if 'initiate' in mode:
        log(output)
    return output


def update_reference(new_path, in_file_or_folder, inc_file=None, mode=0):
    """
    internal function triggered when a .inc file is moved.
     needs to be a separate function to call itself without triggering the rest of the move function
    :param new_path:
    :param in_file_or_folder:
    :param inc_file:
    :param mode:
    :return: logs of updated #include paths
    """
    file_exceptions = [r"O:\Lord of the Mods\_LIBRARY\AotR-override\AOTR8\aotr\data\ini\eva.ini".replace('\\', '/'),
                       r"O:\Lord of the Mods\_LIBRARY\AotR-override\AOTR8\aotr\data\ini\gamelodpresets.ini".replace('\\', '/')]
    folder_exceptions = ["default",
                         "obsolete"]
    output = ''
    line_include = ''
    old_path = ''
    if os.path.isdir(in_file_or_folder):
        folders_paths = os.listdir(in_file_or_folder)
        for folder_path in folders_paths:
            if folder_path in folder_exceptions:
                continue
            output += update_reference(new_path=new_path, in_file_or_folder=f'{in_file_or_folder}/{folder_path}', inc_file=inc_file)
    elif os.path.isfile(in_file_or_folder) and in_file_or_folder.endswith('.ini'):
        if in_file_or_folder in file_exceptions:
            return ''
        line_include += find_replace_text(find=new_path.split('/')[-1], scope=in_file_or_folder, mode='include')
        if line_include:
            old_path = in_file_or_folder
    if old_path:
        output += f'in file {in_file_or_folder}:\n'
        with open(in_file_or_folder) as file_checked:
            lines = file_checked.readlines()
        new_content = ''
        line_counter = 0
        for line in lines:
            line_counter += 1
            if "#include" in line and line.strip()[0] not in INI_COMMENTS and inc_file.lower() in line.lower():
                path_old_include, path_new_include = '', ''
                if line_include in line:
                    path_old_include = line_include.strip()[len('#include "'):line_include.strip().rfind('"')]
                    path_absolute_include = new_path
                    path_new_include = os.path.relpath(path_absolute_include, '/'.join(old_path.split('/')[:-1]))
                elif line_include not in line:
                    path_old_include = line.strip()[len('#include "'):line.strip().rfind('"')]
                    path_absolute_include = os.path.normpath(os.path.join(os.path.dirname(old_path), path_old_include))
                    path_new_include = os.path.relpath(path_absolute_include, '/'.join(old_path.split('/')[:-1]))
                if path_old_include != path_new_include:
                    new_content += line.replace(path_old_include, path_new_include)
                    output += (f'\tin line {line_counter} updated #include "{path_old_include}"'
                               f'\n\t\tto #include "{path_new_include}"\n')
                else:
                    new_content += line
                    output += f'\tin line {line_counter} #include "{path_old_include}" left unchanged.\n'
            else:
                new_content += line
        if ''.join(lines) != new_content and mode == 0:
            with open(in_file_or_folder, 'w') as file_overwritten:
                file_overwritten.write(new_content)
    return output


def update_single_reference(old_path, new_path, mode=0):
    """
    Internal function triggered when a .ini file is moved
    :param old_path:
    :param new_path:
    :param mode: 0 | 1
    :return:
    """
    file_to_open = ''
    if mode == 1:
        file_to_open = old_path
    output = f'in file {file_to_open or new_path}:\n'
    with open(file_to_open or new_path) as file_checked:
        lines = file_checked.readlines()
    new_content = ''
    line_counter = 0
    for line in lines:
        line_counter += 1
        if "#include" in line and line.strip()[0] not in INI_COMMENTS:
            path_old_include = line.strip()[len('#include "'):line.strip().rfind('"')]
            path_absolute_include = os.path.normpath(os.path.join(os.path.dirname(old_path), path_old_include))
            path_new_include = os.path.relpath(path_absolute_include, '/'.join(new_path.split('/')[:-1]))
            if path_old_include != path_new_include:
                new_content += line.replace(path_old_include, path_new_include)
                output += (f'\tin line {line_counter} updated #include "{path_old_include}"'
                           f'\n\t\tto "{path_new_include}"\n')
            else:
                new_content += line
                output += f'\tin line {line_counter} #include "{path_old_include}" left unchanged.\n'
        else:
            new_content += line
    if ''.join(lines) != new_content and mode == 0:
        with open(new_path, 'w') as file_overwritten:
            file_overwritten.write(new_content)
    return output


def move_file(full_path, to_folder, mode=0):
    """moves a given file to a given folder and updates the references to or in this file."""
    output = ''
    file_name = full_path.replace('\\', '/').split('/')[-1]
    to_folder = to_folder.replace('\\', '/')
    if current(MODULES_LIBRARY).replace('\\', '/') not in to_folder:
        # raise InternalError('file_editor.move_file aborted - destination path not in MODS_FOLDER')
        pass
    try:
        if mode == 0:
            output += f'{datetime.now()}'
            output += f' command: move {full_path}\n\tto {to_folder}\n'
            shutil.move(full_path, f'{to_folder}/{file_name}')
        if file_name.endswith('.inc'):
            ini_folder = to_folder[:to_folder.find(INI_PATH_PART) + len(INI_PATH_PART)]
            output += update_reference(new_path=f'{to_folder}/{file_name}', in_file_or_folder=ini_folder, inc_file=file_name)
        elif file_name.endswith('.ini'):
            output += update_single_reference(old_path=full_path, new_path=f'{to_folder}/{file_name}', mode=mode)
    except shutil.Error:
        raise InternalError('file_editor.move_file error: erroneous path')
    log(output)
    return output


# TODO later: look for duplicates in other files too. Objects can be overwritten.
def duplicates_commenter(in_file):
    """
    finds the duplicates in a given file
    :param in_file: string path of the file to load
    :return: logs of the values commented out
    """
    new_content = ''
    output = f'{datetime.now()}'
    output += f' command: comment out duplicates in {in_file}:\n'
    items = load_items(in_file)
    if type(items) is str:
        return items
    items_number = len(items)
    remaining_items_index = 1
    last_result = ''
    for item_index in range(1, items_number):
        to_comment = False
        remaining_items_index += 1
        for remaining_item_index in range(remaining_items_index, items_number):
            if items[item_index].parameter['name'].lower() == items[remaining_item_index].parameter['name'].lower():
                if items[item_index].parameter['class'] == items[remaining_item_index].parameter['class']:
                    to_comment = True
        if to_comment:
            new_content += comment_out(print_items([items[0], items[item_index]])[0])
            last_result = print_items([items[0], items[item_index]])
            output += last_result
        else:
            new_content += print_items([items[0], items[item_index]])
    if not last_result:
        output += 'no duplicate definition found'
    try:
        with open(f'{LOG_PATH}/file_changes.txt', 'a') as log_file:
            log_file.write(output + '\n')
    except FileNotFoundError:
        with open(f'{LOG_PATH}/file_changes.txt', 'w') as log_file:
            log_file.write(output + '\n')
    with open(in_file, 'w') as new_file:
        new_file.write(new_content)
    return output


def load_file(full_path):
    """

    :param full_path: absolute path of the file to load into the text editor
    :return: the file content
    """
    if full_path.endswith('.ini') or full_path.endswith('.str'):
        file_content = print_items(file=full_path)
        try:
            file_levels = recognize_item_class(from_file=full_path)
        except InternalError as error:
            return error.message, []
        return file_content, file_levels
    elif full_path.endswith('.inc'):
        file_content = print_items_part(load_items_part(from_file=full_path))
        try:
            file_levels = recognize_item_class(from_file=full_path)
        except InternalError as error:
            return error.message, []
        return file_content, file_levels
    elif full_path.endswith('.txt'):
        with open(full_path) as loaded_file:
            file_content = loaded_file.read()
            return file_content, []
    else:
        raise TypeError


def load_directories(full_path, mode=0):
    """

    :param full_path:
    :param mode: mode=0 makes the function omit the full path,
     mode=1 makes the function provide the full path of each item
    :return: a tuple of two lists of folders and files contained in the given directory
    """
    output_folders = []
    output_files = []
    try:
        items = os.listdir(full_path)
    except PermissionError as error:
        raise InternalError(error.strerror)
    for item in items:
        if os.path.isdir(f'{full_path}/{item}'):
            output_folders.append(f'{(full_path + "/") * mode}{item}')
            if mode == 1:
                add_folders, add_files = load_directories(output_folders[-1], mode=1)
                if add_folders:
                    output_folders.append(add_folders)
                if add_files:
                    output_files.append(add_files)
        elif os.path.isfile(f'{full_path}/{item}'):
            output_files.append(f'{(full_path + "/") * mode}{item}')
    return output_folders, output_files


_all_defined = [
    convert_string,
    find_replace_text,
    update_reference,
    update_single_reference,
    move_file,
    duplicates_commenter,
    load_file,
    load_directories,
]
