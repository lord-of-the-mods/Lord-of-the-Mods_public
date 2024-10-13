import os.path
import shutil
import tkinter
import winreg
import json
from tkinter.filedialog import askdirectory
from tkinter.messagebox import askyesnocancel, showerror, showwarning
from sys import exit

from constants import PROGRAM_NAME, InternalError, load_delimiters
from settings import settings_read, settings_save_to_file, SETTINGS_PATH
from module_control import definition_write

# import PyInstaller
#
# PyInstaller.PYINSTALLER_SUPPRESS_SPLASH_SCREEN = 1

default_folders_dict = {
    'library': './_LIBRARY',
    'archive': './_ARCHIVE',
}

if os.path.isfile('./initial/_games.json'):
    with open('./initial/_games.json') as games_buffer:
        game_list = json.load(games_buffer)
else:
    # raise InternalError('initial games data', 'missing')
    pass


# 024-08-26
def search_reg(master_key_name, game_name):
    """ Looks for the game installation paths in the Windows Registry. """
    registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    output = ''
    try:
        master_key = winreg.OpenKey(registry, master_key_name)
        for reg_key_index in range(winreg.QueryInfoKey(master_key)[0]):
            child_key_name = winreg.EnumKey(master_key, reg_key_index)
            new_master = f'{master_key_name}\\{child_key_name}'
            if child_key_name == game_name:
                child_key = winreg.OpenKey(master_key, child_key_name)
                try:
                    install_directory = winreg.QueryValueEx(child_key, 'InstallPath')[0]
                    if install_directory.endswith('\\'):
                        install_directory = install_directory[:-1]
                    output += install_directory.replace('\\', '/')  # + '\n'
                except FileNotFoundError:
                    continue
            else:
                output += f'{search_reg(new_master, game_name)}'
    except PermissionError:
        pass
    return output


def get_game_directory():
    """ Returns a list of game paths. """
    game_directories = []
    try:
        for game_key in game_list:
            try:
                game_directories.append(search_reg(game_key['Registry'], game_key['Name']))
            except FileNotFoundError:
                # try:
                #     game_directories.append(search_reg('SOFTWARE', game_key['Name']))
                # except FileNotFoundError:
                provided_directory = askdirectory(
                    title=f"{PROGRAM_NAME}: please select {game_key['Name']} directory (or create one)",
                    initialdir='../')
                if provided_directory:
                    game_directories.append(provided_directory)
                else:
                    cancel_initiation()
    except NameError:
        raise InternalError
    for game_index in range(len(game_directories)):
        if os.path.isdir(game_directories[game_index]):
            game_directories[game_index] = os.path.relpath(game_directories[game_index]).replace('\\', '/')
    return game_directories


def ensure_game_options():
    """ Copies files necessary to run the game. """
    try:
        for game_key in game_list:
            try:
                roaming_path = os.path.expanduser(f"~{game_key['Roaming']}")
                if not os.path.isdir(roaming_path):
                    os.mkdir(roaming_path)
                for roaming_file in game_key['RoamingFiles']:
                    if not os.path.isfile(f'{roaming_path}/{roaming_file}'):
                        shutil.copy(
                            f"./initial/{game_key['Roaming'].split('/')[-1]}/{roaming_file}", roaming_path)
            except FileNotFoundError:
                pass
    except NameError:
        pass


def cancel_initiation():
    """ Triggered when the directories are not provided to terminate the window. """
    showerror(
        title=f'{PROGRAM_NAME} initiator: Error',
        message='The program cannot function properly without the appropriate settings\n Please try again'
    )
    exit()


def copy_default(new_directory, initial_dir='./initial/default_module_template'):
    """
    Copies the files from the initial_dir into the new directory
    :param new_directory: current LIBRARY path
    :param initial_dir: directory to copy from
    :return:
    """
    if not os.path.isdir(new_directory):
        os.mkdir(new_directory)
    if os.path.isdir(initial_dir):
        for file_or_folder in os.listdir(initial_dir):
            if (os.path.isfile(f'{initial_dir}/{file_or_folder}')
                    and not os.path.isfile(f'{new_directory}/{file_or_folder}')):
                shutil.copy(f'{initial_dir}/{file_or_folder}', new_directory)
            elif os.path.isdir(f'{initial_dir}/{file_or_folder}'):
                if not os.path.isdir(f'{new_directory}/{file_or_folder}'):
                    os.mkdir(f'{new_directory}/{file_or_folder}')
                copy_default(
                    new_directory=f'{new_directory}/{file_or_folder}',
                    initial_dir=f'{initial_dir}/{file_or_folder}'
                )
    else:
        pass


def initiate():
    """ Initiates the application settings by asking for directories needed by the application. """
    initiator = tkinter.Tk()
    initiator.iconbitmap('aesthetic/icon.ico')
    initiator.title(f'{PROGRAM_NAME} initiator')
    initiator.minsize(width=500, height=200)
    initiator_label = tkinter.Label(master=initiator, text='Looking for game paths. Please wait...')
    initiator_label.pack()
    initiator.update()
    if not os.path.isfile(SETTINGS_PATH):
        try:
            game_paths_list = get_game_directory()
        except InternalError:
            game_paths_list = []
        directories_dict = {}
        initiator_label.configure(text='Initiating functional directories.')
        initiator.update()
        use_default_paths = askyesnocancel(
            title=f'{PROGRAM_NAME} initiator:',
            message=f'Use default functional folder names? If not, you can choose your own.'
        )
        if use_default_paths is True:
            for key in default_folders_dict:
                directories_dict[key] = default_folders_dict[key]
        if use_default_paths is False:
            for key in default_folders_dict:
                evaluated_string = askdirectory(
                    title=f'{PROGRAM_NAME} initiator: Please select the module {key} directory\n',
                    initialdir='./'
                )
                if os.path.isdir(evaluated_string):
                    directories_dict[key] = os.path.relpath(evaluated_string).replace('\\', '/')
                else:
                    showwarning(
                        title=f'{PROGRAM_NAME} initiator: ',
                        message=f'The provided name is empty.\n'
                                f' The default value will be applied'
                    )
                    directories_dict[key] = default_folders_dict[key]
        elif use_default_paths is None:
            cancel_initiation()
        copy_default(directories_dict['library'])
        settings_save_to_file(
            do_initiate=True,
            ModulesLibrary=directories_dict['library'],
            ArchiveFolder=directories_dict['archive'],
            ModuleDefaultTemplate=f"{directories_dict['library']}/__empty template",
            GamePaths=game_paths_list,
        )
        initiator_label.configure(text='Creating initial modules. Please wait ...')
        initiator.update()
        for game_path in game_paths_list:
            try:
                # module_copy(new_name=game_path.split('/')[-1],
                #             template_directory=f"{directories_dict['library']}/__empty template",
                #             changes_source=game_path)
                # definition_edit(module_path=f"{directories_dict['library']}/{game_path.split('/')[-1]}",
                #                 description=f"Initial {game_path.split('/')[-1]} - created automatically")
                if not os.path.isdir(f"{directories_dict['library']}/{game_path.split('/')[-1]}"):
                    os.mkdir(f"{directories_dict['library']}/{game_path.split('/')[-1]}")
                definition_write(module_directory=f"{directories_dict['library']}/{game_path.split('/')[-1]}",
                                 return_type='object save', changes_source=game_path,
                                 description=f"Initial {game_path.split('/')[-1]} - created automatically")
            except InternalError:
                pass
    else:
        settings_read('initiate')
        # pass
    # process_constants()
    ensure_game_options()
    load_delimiters()
    initiator.destroy()


_all_defined = [
    # initiate_game_data,
    search_reg,
    get_game_directory,
    ensure_game_options,
    cancel_initiation,
    initiate,
]
