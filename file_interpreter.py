from constants import INI_COMMENTS, INI_ENDS, LEVEL_INDENT, InternalError, INI_DELIMITERS, STR_DELIMITERS
from module_control import DEFINITION_NAME


def recognize_item_class(from_file):
    if from_file.replace('\\', '/').split('/')[-1] == DEFINITION_NAME:
        raise InternalError('functional file')
    file_item_type = []
    if from_file.endswith('.str'):
        file_item_type = STR_DELIMITERS
    elif from_file.endswith('.ini'):
        with open(from_file) as loaded_file:
            # while not file_item_type:
            #     word = loaded_file.readline().split()
            file_lines = loaded_file.readlines()
            for file_line in file_lines:
                if file_item_type:
                    break
                words = file_line.split()
                if len(words) > 0:
                    for items_levels in INI_DELIMITERS:
                        if words[0] in items_levels[0]:
                            file_item_type = items_levels
                            break
    elif from_file.endswith('.inc'):
        with open(from_file) as loaded_file:
            # while not file_item_type:
            #     words = loaded_file.readline().split()
            for file_line in loaded_file.readlines():
                words = file_line.split()
                if len(words) > 0:
                    for items_levels in INI_DELIMITERS:
                        for item_level in items_levels:
                            if words[0] in item_level:
                                file_item_type = items_levels
                                break
    file_item_type.append([])
    return file_item_type


def load_items(from_file, mode=0):
    """
     loads and reformats items like an Object or an ObjectCreationList defined in an INI or STR file
    :param from_file: the full path of the source file to read the objects from
    :param mode: mode=1 enables to exit at the first error with the object list created so far
    :return: loaded items in form of a list of ItemLevel objects where the first describes the source file
    """
    if not from_file:
        return 'file_interpreter: load_items error: no file selected'
    items = [[{'class': 'file'}]]
    items[0][0]['name'] = from_file
    try:
        file_item_type = recognize_item_class(from_file)
    except InternalError as error:
        raise error
    items[0].append({'structure': file_item_type})
    current_level = 0
    initial_comment = ''
    line_counter = 0
    is_level_open = False
    is_definition_open = False
    with open(from_file) as loaded_file:
        file_lines = loaded_file.readlines()
    for file_line in file_lines:
        line_counter += 1
        try:
            words = file_line.replace('=', ' ').replace(':', ' ').split()
            if file_line.strip() == '':
                continue
            elif file_line.strip()[0] in INI_COMMENTS:
                if not is_definition_open:  # not is_level_open
                    initial_comment += ' '.join(file_line.split()) + '\n'
                elif current_level == 1:
                    items[-1].append({'comment': f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"})
                elif current_level > 1:
                    items[-1][-1].append(
                        {'comment': f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"}
                    )
            # elif words[0].rstrip(';/') in file_item_type[current_level]:
            elif words[0].replace('/', ' ').replace(';', ' ').split()[0].strip() in file_item_type[current_level]:
                if current_level == 0:
                    items.append([{}, {'class': 'words[0]'}])
                    items[-1][1]['class'] = words[0]
                    is_definition_open = True
                    if len(words) >= 2:
                        if words[1][0] not in INI_COMMENTS:
                            items[-1][1]['name'] = words[1]
                            if len(words) >= 3:
                                if words[2][0] not in INI_COMMENTS:
                                    items[-1][-1]['identifier'] = words[2]
                                    if len(words) > 3 and words[3][0] in INI_COMMENTS:
                                        items[-1][-1]['comment'] = (
                                            f'{LEVEL_INDENT * current_level}'
                                            f'{file_line[file_line.index(words[3]):]}'
                                        )
                                elif words[2][0] in INI_COMMENTS:
                                    items[-1][-1]['comment'] = ' '.join(words[2:])
                        elif words[1][0] in INI_COMMENTS:
                            items[-1][-1]['comment'] = ' '.join(words[1:])
                elif current_level == 1:
                    items[-1].append([])
                    items[-1][-1].append({'class': words[0]})
                    is_level_open = True
                    if len(words) >= 2:
                        if words[1][0] not in INI_COMMENTS:
                            items[-1][-1][0]['name'] = words[1]
                            if len(words) >= 3:
                                if words[2][0] not in INI_COMMENTS:
                                    items[-1][-1][0]['identifier'] = words[2]
                                    if len(words) > 3 and words[3][0] in INI_COMMENTS:
                                        items[-1][-1][0]['comment'] = (
                                            f'{LEVEL_INDENT * current_level}'
                                            f'{file_line[file_line.index(words[3]):]}'
                                        )
                                elif words[2][0] in INI_COMMENTS:
                                    # items[-1][-1]['comment'] = ' '.join(words[2:])
                                    if isinstance(items[-1], list):
                                        if isinstance(items[-1][-1], list):
                                            items[-1][-1][-1]['comment'] = ' '.join(words[2:])
                                        else:
                                            items[-1][-1]['comment'] = ' '.join(words[2:])
                        elif words[1][0] in INI_COMMENTS:
                            if isinstance(items[-1], list):
                                if isinstance(items[-1][-1], list):
                                    items[-1][-1][-1]['comment'] = ' '.join(words[1:])
                                else:
                                    items[-1][-1]['comment'] = ' '.join(words[1:])
                elif current_level > 1:
                    try:
                        if is_level_open:
                            items[-1][-1].append(
                                {'assignation': f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"}
                            )
                    except AttributeError:
                        items[-1].append(
                            {'assignation': f"{LEVEL_INDENT}{' '.join(file_line.split())}\n"}
                        )
                current_level += 1
            elif words[0].rstrip(';/') in INI_ENDS:
                current_level -= 1
                if current_level == 0:
                    items[-1][0]['comment'] = initial_comment
                    initial_comment = ''
                    is_definition_open = False
                elif current_level == 1:
                    is_level_open = False
                elif current_level > 1:
                    try:
                        if is_level_open:
                            items[-1][-1].append(
                                {'assignation': f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"}
                            )
                    except AttributeError:  # IndexError:
                        items[-1].append(
                            {'assignation': f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"}
                        )
            elif is_definition_open:
                try:
                    if is_level_open:
                        items[-1][-1].append(
                            {'assignation': f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"}
                        )
                    else:
                        items[-1].append(
                            {'assignation': f"{LEVEL_INDENT}{' '.join(file_line.split())}\n"}
                        )
                except AttributeError:
                    items[-1].append(
                        {'assignation': f"{LEVEL_INDENT}{' '.join(file_line.split())}\n"}
                    )
            elif words[0] == '#define':
                # if items[0][0]['defines']:
                if 'defines' in items[0][0]:
                    items[0][0]['defines'] += file_line.strip() + '\n'
                else:
                    items[0][0]['defines'] = file_line.strip() + '\n'
            elif words[0] == '#include':
                # TODO: manage free includes
                pass
            else:
                if mode == 1:
                    return items
                print(f'file interpreter: load_items() exception: file {from_file}, line: {line_counter}\n{file_line}')
            if file_line.strip().startswith('AddEmotion'):
                if words[:2] == ['AddEmotion', 'OVERRIDE']:
                    current_level += 1
        except IndexError as error:
            print(error)
    return items


def load_items_part(from_file, mode=0):
    """
     loads and reformats items like an Object or an ObjectCreationList defined in an INI or STR file
    :param from_file: the full path of the source file to read the objects from
    :param mode: mode=1 enables to exit at the first error with the object list created so far
    :return: loaded items in form of a list of ItemLevel objects where the first describes the source file
    """
    if not from_file:
        return 'file_interpreter: load_items error: no file selected'
    items = [[{'class': 'file'}]]
    items[0][0]['name'] = from_file
    try:
        file_item_type = recognize_item_class(from_file)
    except InternalError as error:
        raise error

    start_level = 0
    initial_comment = ''
    # line_counter = 0
    is_level_open = False
    is_definition_open = False
    with open(from_file) as loaded_file:
        file_lines = loaded_file.readlines()
    for file_line in file_lines:
        words = file_line.replace('=', ' ').replace(':', ' ').split()
        if file_line.strip() == '':
            continue
        elif file_line.strip()[0] in INI_COMMENTS:
            continue
        elif words[0].rstrip(';/') in INI_ENDS:
            continue
        else:
            for level in file_item_type:
                if words[0].rstrip(';/') in level:
                    start_level = file_item_type.index(level)
                    break
            break
    items[0].append({'structure': file_item_type})
    current_level = start_level
    for file_line in file_lines:
        # line_counter += 1
        words = file_line.replace('=', ' ').replace(':', ' ').split()
        if file_line.strip() == '':
            continue
        elif file_line.strip()[0] in INI_COMMENTS:
            if not is_definition_open:  # not is_level_open
                initial_comment += f'{LEVEL_INDENT * current_level}' + ' '.join(file_line.split()) + '\n'  #
            elif current_level - start_level >= 1:
                items[-1].append({'comment': f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"})  #
            # elif current_level - start_level > 1:
            #     items[-1][-1]['comment'] = f"{' '.join(file_line.split())}\n"  # {LEVEL_INDENT * current_level}
        elif words[0].rstrip(';/') in file_item_type[current_level]:
            if current_level - start_level == 0:
                items.append([{}, {'indent': LEVEL_INDENT * current_level, 'class': words[0]}])  # 'indent': f'{LEVEL_INDENT * current_level}'
                # items[-1][1]['class'] = words[0]
                is_definition_open = True
                if len(words) >= 2:
                    if words[1][0] not in INI_COMMENTS:
                        items[-1][1]['name'] = words[1]
                        if len(words) >= 3:
                            if words[2][0] not in INI_COMMENTS:
                                items[-1][-1]['identifier'] = words[2]
                                if len(words) > 3 and words[3][0] in INI_COMMENTS:
                                    items[-1][-1]['comment'] = (
                                        f'{LEVEL_INDENT * current_level}'
                                        f'{file_line[file_line.index(words[3]):]}'
                                    )
                            elif words[2][0] in INI_COMMENTS:
                                items[-1][-1]['comment'] = ' '.join(words[2:])
                    elif words[1][0] in INI_COMMENTS:
                        items[-1][-1]['comment'] = ' '.join(words[1:])
                is_level_open = True
            # elif current_level - start_level == 1:
            #     items[-1].append([])
            #     items[-1][-1].append({'class': words[0]})
            #     if len(words) >= 2:
            #         if words[1][0] not in INI_COMMENTS:
            #             items[-1][-1][0]['name'] = words[1]
            #             if len(words) >= 3:
            #                 if words[2][0] not in INI_COMMENTS:
            #                     items[-1][-1][0]['identifier'] = words[2]
            #                     if len(words) > 3 and words[3][0] in INI_COMMENTS:
            #                         items[-1][-1][0]['comment'] = (
            #                             f'{LEVEL_INDENT * current_level}'
            #                             f'{file_line[file_line.index(words[3]):]}'
            #                         )
            #                 elif words[2][0] in INI_COMMENTS:
            #                     # items[-1][-1]['comment'] = ' '.join(words[2:])
            #                     if isinstance(items[-1], list):
            #                         if isinstance(items[-1][-1], list):
            #                             items[-1][-1][-1]['comment'] = ' '.join(words[2:])
            #                         else:
            #                             items[-1][-1]['comment'] = ' '.join(words[2:])
            #         elif words[1][0] in INI_COMMENTS:
            #             if isinstance(items[-1], list):
            #                 if isinstance(items[-1][-1], list):
            #                     items[-1][-1][-1]['comment'] = ' '.join(words[1:])
            #                 else:
            #                     items[-1][-1]['comment'] = ' '.join(words[1:])
            elif current_level - start_level >= 1:
                try:
                    if is_level_open:
                        items[-1][-1].append(
                            {'assignation': f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"}
                        )
                except AttributeError:
                    items[-1].append(
                        {'assignation': f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"}
                    )
            current_level += 1
        elif words[0].rstrip(';/') in INI_ENDS:
            current_level -= 1
            if current_level - start_level == 0:
                items[-1][0]['comment'] = f'{initial_comment}'
                initial_comment = ''
                is_definition_open = False
                is_level_open = False
                items[-1].append({'end': f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"})
            # elif current_level - start_level == 1:
            elif current_level - start_level >= 1:
                try:
                    if is_level_open:
                        items[-1][-1].append(
                            {'assignation': f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"}
                        )
                except AttributeError:  # IndexError:
                    items[-1].append(
                        {'assignation': f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"}
                    )
        elif is_definition_open:
            try:
                if is_level_open:
                    items[-1][-1].append(
                        {'assignation': f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"}
                    )
                else:
                    items[-1].append(
                        {'assignation': f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"}
                    )
            except AttributeError:
                items[-1].append(
                    {'assignation': f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"}
                )
        else:
            if mode == 1:
                return items
            print('file interpreter: load_items() exception: ' + file_line)
    return items


def print_items(items=None, file=None):
    """
     concatenates a string from loaded items like an Object or an ObjectCreationList defined in an INI or STR file
    :param items: loaded items as a list of object returned by the load_items() function
    :param file:
    :return: printable string being the reformatted content of a file
    """
    if file and not items:
        try:
            items = load_items(file)
        except InternalError as error:
            raise error
    output = ''
    levels_list = []
    splitter = ' '
    if items[0][0]['class'] == 'file':
        levels_list = items[0][1]['structure']
        if items[0][0]['name'].endswith('.str'):
            splitter = ':'
        if 'defines' in items[0][0]:
            output += items[0][0]['defines']
    for item in items[1:]:
        if item[1]['class'] in levels_list[0]:
            for index in range(0, len(item)):
                try:
                    if type(item[index]) is list:
                        for level_index in range(len(item[index])):
                            if type(item[index][level_index]) is dict:
                                line = ''  # LEVEL_INDENT
                                for key in item[index][level_index]:
                                    line += ' ' + item[index][level_index][key]
                                if line[0:len(LEVEL_INDENT)] != LEVEL_INDENT:
                                    line = LEVEL_INDENT + line
                                if line[-1] != '\n':
                                    line += '\n'
                                output += line[1:]
                            else:
                                output += item[index][level_index]
                        output += f'{LEVEL_INDENT}End\n'
                    elif type(item[index]) is dict:
                        line = ' '
                        for key in item[index]:
                            line += splitter + item[index][key]
                        if line[-1] != '\n':
                            line += '\n'
                        output += line[2:]
                    else:
                        output += item[index]
                except KeyError:
                    print('file_interpreter: print_items() error: KeyError')
            output += 'End\n\n'
    return output


def print_items_part(items=None, file=None):
    """
     concatenates a string from loaded items like an Object or an ObjectCreationList defined in an INI or STR file
    :param items: loaded items as a list of object returned by the load_items() function
    :param file:
    :return: printable string being the reformatted content of a file
    """
    if file and not items:
        try:
            items = load_items(file)
        except InternalError as error:
            raise error
    output = ''
    # levels_list = []
    # if items[0][0]['class'] == 'file':
    #     levels_list = items[0][1]['structure']
    for item in items[1:]:
        current_level = output.rstrip().split('\n')[-1].count(LEVEL_INDENT)
        for index in range(len(item)):
            if type(item[index]) is dict:
                line = ''
                for key in item[index]:
                    if line.strip():
                        line += ' ' + item[index][key]
                    else:
                        line += item[index][key]
                if not line.strip():
                    continue
                if not line.startswith(LEVEL_INDENT * current_level) and line.split()[-1] not in INI_ENDS:
                    line = f'{LEVEL_INDENT * current_level}{line.lstrip()}'
                if line[-1] != '\n':
                    line += '\n'
                output += line
    return output


def comment_out(lines):
    """
    comments out a few lines in a loaded and printed item
    :param lines:
    :return:
    """
    output = ''
    for line in lines.split('\n'):
        output += f';;;{line}\n'
    return output


_all_defined = [
    recognize_item_class,
    load_items,
    load_items_part,
    print_items,
    print_items_part,
    comment_out,
]
