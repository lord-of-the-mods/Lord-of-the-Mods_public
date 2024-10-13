import os.path
import json

from constants import InternalError

SETTINGS_PATH = './_settings.json'

INSTALL_PATH = '0'
MODULES_LIBRARY = '1'
BACKUP_FOLDER = '2'
MODULE_TEMPLATE = '3'

CONSTANTS_DICT = {
    INSTALL_PATH: '../',
    MODULES_LIBRARY: 'ModulesLibrary',
    BACKUP_FOLDER: 'ArchiveFolder',
    MODULE_TEMPLATE: 'ModuleDefaultTemplate',
}

settings_format = {}


def settings_get_format():
    global settings_format
    if os.path.isfile('./initial/_settings_format.json'):
        with open('./initial/_settings_format.json') as settings_buffer:
            settings_format = json.load(settings_buffer)
    else:
        raise InternalError('settings initial file', 'missing')


settings_get_format()


def current(setting_key):
    settings = settings_read()
    try:
        if settings[CONSTANTS_DICT[setting_key]]:
            output = (os.path.abspath(settings[CONSTANTS_DICT[setting_key]])).replace('\\', '/')
        else:
            raise InternalError('Settings not loaded')
    except KeyError:
        if CONSTANTS_DICT[setting_key]:
            output = (os.path.abspath(CONSTANTS_DICT[setting_key])).replace('\\', '/')
        else:
            raise InternalError('Settings not loaded')
    return output


def settings_read(return_type='dict', settings_dict=None):
    """
    Checks the parameters of the SETTINGS_FILE against any deviations from the hardcoded form of the settings.ini
    :param settings_dict:
    :param return_type: 'dict' (default) | 'initiate' | 'check'
    :return: a list of lines being the split SETTINGS_FILE if it is correct or being valueless if incorrect
    """
    if settings_dict is None and os.path.isfile(SETTINGS_PATH):
        with open(SETTINGS_PATH) as settings_buffer:
            settings_dict = json.load(settings_buffer)
    if settings_dict is None and settings_format:
        if return_type == 'dict':
            return settings_format
    elif settings_dict is None:
        raise InternalError
    else:
        for key in settings_dict:
            if key == 'comment' or key == 'title' or key == 'version' or key == 'LibraryExceptions':
                pass
            elif settings_dict[key]:
                if isinstance(settings_dict[key], list):
                    for path in settings_dict[key]:
                        if path and not os.path.isdir(path):
                            if return_type == 'check':
                                raise InternalError(path, 'missing')
                            elif return_type == 'initiate':
                                os.mkdir(path)
                elif isinstance(settings_dict[key], str):
                    if not os.path.isdir(settings_dict[key]):
                        if return_type == 'check':
                            raise InternalError(settings_dict[key], 'missing')
                        elif return_type == 'initiate':
                            os.mkdir(settings_dict[key])
                else:
                    if return_type == 'check':
                        raise InternalError(settings_dict[key], 'missing')
            else:
                # print(f'missing value for key: {key}')
                pass
        if return_type == 'dict':
            return settings_dict


def settings_save_to_file(settings_dict=None, do_initiate=False, **keyword_settings):
    """
    Saves the values provided (inserted in the application) to the SETTING_FILE.
    Then it checks if the new settings are valid. If not, retrieves the backed up settings.
    :param do_initiate:
    :param settings_dict: settings organized in a dictionary
    :param keyword_settings: settings as key-word arguments-values pairs
    :return: string sentence about success or failure to find the paths provided
    """
    if not keyword_settings and settings_dict is not None:
        keyword_settings = settings_dict
    settings_json = settings_read()
    settings_json_new = {}
    for key in settings_json:
        if key in keyword_settings:
            if isinstance(keyword_settings[key], str) and isinstance(settings_json[key], str):
                settings_json_new[key] = keyword_settings[key]
            elif isinstance(keyword_settings[key], str) and isinstance(settings_json[key], list):
                settings_json_new[key] = settings_json[key]
                settings_json_new[key].append(keyword_settings[key])
            elif isinstance(keyword_settings[key], list) and isinstance(settings_json[key], list):
                settings_json_new[key] = keyword_settings[key]
        else:
            settings_json_new[key] = settings_json[key]
    try:
        if do_initiate:
            settings_read(return_type='initiate', settings_dict=settings_json_new)
        else:
            settings_read(return_type='check', settings_dict=settings_json_new)
        with open(SETTINGS_PATH, 'w') as settings_buffer:
            settings_buffer.write(json.dumps(settings_json_new, indent=4))
        return 'settings saved and checked.'
    except InternalError:
        return 'settings.settings_save error: the provided value seems to be incorrect.'


_all_defined = [
    settings_get_format,
    current,
    settings_read,
    settings_save_to_file
]
