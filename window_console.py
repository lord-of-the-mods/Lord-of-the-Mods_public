import os.path
import tkinter
import _tkinter
from tkinter.messagebox import askquestion
from tkinter.filedialog import askopenfilenames, askdirectory
from tkinter.ttk import Treeview
from tklinenums import TkLineNumbers
from ctypes import windll, byref, create_unicode_buffer, sizeof, c_int

from constants import INI_COMMENTS, INI_ENDS, LEVEL_INDENT, PROGRAM_NAME, InternalError
from initiator import initiate
from settings import settings_read, settings_save_to_file, current, MODULES_LIBRARY, INSTALL_PATH
from file_editor import convert_string, find_replace_text, move_file, duplicates_commenter, load_file, \
    load_directories
from module_control import modules_filter, modules_sort, snapshot_take, snapshot_compare, game_names, \
    module_detect_changes, module_copy, detect_new_modules, \
    definition_edit, DEFINITION_EXAMPLE, DEFINITION_NAME, DEFINITION_CLASSES

UNIT_WIDTH = 80
UNIT_HEIGHT = 40
TEXT_WIDTH = UNIT_WIDTH * 12
FULL_WIDTH = UNIT_WIDTH * 15
LIST_WIDTH = 160
MODULE_COLUMNS = ('name', 'class', 'progress', 'description')

global_modules = []
current_path = ''
current_levels = []
current_file_content_backup = ''
current_window = ''
new_module_name = ''
new_module_source = ''


# TODO later: class ReactiveButton that reacts to hover and press through binding and shows info on hover
class ReactiveButton(tkinter.Button):
    pass


class NewModuleDialog(tkinter.Toplevel):
    """ a Tk/TCl Toplevel-based class """
    def __init__(self, **kw):
        super().__init__(**kw)
        self.title = f'{PROGRAM_NAME}: new module initiator'
        self.iconbitmap('aesthetic/icon.ico')
        self.geometry('320x360')
        self.resizable(False, False)
        self.configure(background=APP_BACKGROUND_COLOR)
        set_title_bar_color(self)

        self.name_label = tkinter.Label(master=self)
        self.name_label.place(x=UNIT_WIDTH * 0, y=UNIT_HEIGHT*0, width=UNIT_WIDTH * 4, height=UNIT_HEIGHT)
        self.name_label.configure(
            background=ENTRY_BACKGROUND_COLOR, foreground=TEXT_COLORS[0], text='Please provide the new module name')
        self.name_entry = tkinter.Entry(master=self)
        self.name_entry.place(x=int(UNIT_WIDTH*0.5), y=UNIT_HEIGHT * 1, width=UNIT_WIDTH * 3, height=UNIT_HEIGHT)
        self.name_entry.configure(background=ENTRY_BACKGROUND_COLOR, foreground=TEXT_COLORS[0])
        self.options_label = tkinter.Label(master=self)
        self.options_label.place(x=UNIT_WIDTH * 0, y=UNIT_HEIGHT * 3, width=UNIT_WIDTH * 4, height=UNIT_HEIGHT)
        self.options_label.configure(
            background=ENTRY_BACKGROUND_COLOR, foreground=TEXT_COLORS[0],
            text='Please choose the definition creation mode')
        self.options_container = tkinter.Frame(master=self)
        self.options_container.place(x=int(UNIT_WIDTH*0.5), y=UNIT_HEIGHT*4, width=UNIT_WIDTH*3, height=UNIT_HEIGHT*3)
        self.options_container.configure(background=ENTRY_BACKGROUND_COLOR)
        self.variable_option = tkinter.StringVar()
        option_button_a = tkinter.Checkbutton(
            master=self.options_container, text='present directory', variable=self.variable_option, onvalue='directory')
        option_button_a.place(x=UNIT_WIDTH * 0, y=UNIT_HEIGHT * 0, width=2 * UNIT_WIDTH, height=UNIT_HEIGHT)
        option_button_a.configure(background=ENTRY_BACKGROUND_COLOR, foreground=TEXT_COLORS[0],
                                  activebackground=APP_BACKGROUND_COLOR, activeforeground=TEXT_COLORS[0],
                                  selectcolor=ENTRY_BACKGROUND_COLOR)
        option_button_b = tkinter.Checkbutton(
            master=self.options_container, text='comparison', variable=self.variable_option, onvalue='comparison')
        option_button_b.place(x=UNIT_WIDTH * 0, y=UNIT_HEIGHT * 1, width=2 * UNIT_WIDTH, height=UNIT_HEIGHT)
        option_button_b.configure(background=ENTRY_BACKGROUND_COLOR, foreground=TEXT_COLORS[0],
                                  activebackground=APP_BACKGROUND_COLOR, activeforeground=TEXT_COLORS[0],
                                  selectcolor=ENTRY_BACKGROUND_COLOR)
        option_button_c = tkinter.Checkbutton(
            master=self.options_container, text='snapshot', variable=self.variable_option, onvalue='snapshot')
        option_button_c.place(x=UNIT_WIDTH * 0, y=UNIT_HEIGHT * 2, width=2 * UNIT_WIDTH, height=UNIT_HEIGHT)
        option_button_c.configure(
            background=ENTRY_BACKGROUND_COLOR, foreground=TEXT_COLORS[0], selectcolor=ENTRY_BACKGROUND_COLOR,
            activebackground=APP_BACKGROUND_COLOR, activeforeground=TEXT_COLORS[0])
        option_button_a.select()

        self.ok_button = tkinter.Button(master=self, text='run', command=self.return_entry)
        self.ok_button.place(x=int(UNIT_WIDTH*0.5), y=int(UNIT_HEIGHT * 7.5), width=UNIT_WIDTH, height=UNIT_HEIGHT)
        self.ok_button.configure(
            background=APP_BACKGROUND_COLOR, foreground=TEXT_COLORS[0], image=image_button_small_idle,
            activebackground=APP_BACKGROUND_COLOR, borderwidth=0, compound='center'
        )
        self.cancel_button = tkinter.Button(master=self, text='cancel', command=self.return_cancel)
        self.cancel_button.place(x=int(UNIT_WIDTH*2.5), y=int(UNIT_HEIGHT*7.5), width=UNIT_WIDTH, height=UNIT_HEIGHT)
        self.cancel_button.configure(
            background=APP_BACKGROUND_COLOR, foreground=TEXT_COLORS[0], image=image_button_small_idle,
            activebackground=APP_BACKGROUND_COLOR, borderwidth=0, compound='center'
        )
        self.protocol("WM_DELETE_WINDOW", self.return_cancel)
        self.mainloop()

    def return_entry(self):
        global new_module_name, new_module_source
        all_module_names = modules_filter(return_type='names')
        if self.name_entry.get() and self.variable_option.get() and self.name_entry.get() not in all_module_names:
            new_module_name = self.name_entry.get()
            new_module_source = self.variable_option.get()
            self.quit()
            self.destroy()
        else:
            self.name_label.configure(text=' Please provide a name unique to the new module')

    def return_cancel(self):
        global new_module_name, new_module_source
        new_module_name, new_module_source = '', ''
        self.quit()
        self.destroy()


def set_title_bar_color(window):
    """based on https://stackoverflow.com/questions/67444141/how-to-change-the-title-bar-in-tkinter"""
    window.update()
    hwnd = windll.user32.GetParent(window.winfo_id())
    dwmwa_caption_color = 35
    color_r = int(APP_BACKGROUND_COLOR[1:3], base=16)
    color_g = int(APP_BACKGROUND_COLOR[3:5], base=16)
    color_b = int(APP_BACKGROUND_COLOR[5:7], base=16)
    reformatted_color = color_b * 16 ** 4 + color_g * 16 ** 2 + color_r
    windll.dwmapi.DwmSetWindowAttribute(hwnd, dwmwa_caption_color, byref(c_int(reformatted_color)), sizeof(c_int))


class ColumnedListbox(tkinter.ttk.Treeview):
    """ a Tk/Tcl Treeview-based class with predefined columns"""

    def __init__(self, master, width, height, show='tree headings'):  # , **kw
        super().__init__(master=master, height=height, show=show)
        self.width = width * 6
        self.columns_list = MODULE_COLUMNS
        self.build_list()
        self.set_columns_proportions(proportions=(1, 1, 1, 5))

    def build_list(self):
        self.configure(columns=self.columns_list)
        for column in self.columns_list:
            self.heading(column, text=column)

    def set_columns_proportions(self, proportions):
        total_quotient = sum(proportions, 1)
        self.column('#0', width=int(self.width / total_quotient))
        for column_index in range(len(proportions)):
            self.column(
                self.columns_list[column_index],
                width=int(self.width / total_quotient * proportions[column_index])
            )
            if column_index == len(proportions) - 1:
                self.column(
                    self.columns_list[column_index],
                    width=int(self.width / total_quotient * proportions[column_index]) - 5
                )

    def open_children(self):
        for search_index in range(10):
            open_children(self, parent=str(search_index))


def open_children(tree, parent):
    """ Recurring function to display all modules hierarchically. """
    try:
        tree.item(parent, open=True)
        for child in tree.get_children(parent):
            open_children(tree, child)
    except _tkinter.TclError:
        pass


def load_font(font_path):
    """
    Loads the given font into the application.
    :param font_path: path to the font.
    :return: True if the font has been loaded. False otherwise.
    """
    '''based on https://stackoverflow.com/questions/11993290/truly-custom-font-in-tkinter'''
    # https://github.com/ifwe/digsby/blob/f5fe00244744aa131e07f09348d10563f3d8fa99/digsby/src/gui/native/win/winfonts.py#L15
    if os.path.isfile(font_path):
        path_buf = create_unicode_buffer(font_path)
        flags = (0x10 | 0)
        num_fonts_added = windll.gdi32.AddFontResourceExW(byref(path_buf), flags, 0)
        return bool(num_fonts_added)
    else:
        return False


if load_font('./aesthetic/Albertus MT Light.ttf'):
    FONT_TEXT = ('Albertus MT Light', 11, 'normal')
    FONT_BUTTON = ('Albertus MT Light', 10, 'normal')
else:
    FONT_TEXT = ('Lato', 11, 'normal')
    FONT_BUTTON = ('Lato', 11, 'normal')

APP_BACKGROUND_COLOR = 'grey'
ENTRY_BACKGROUND_COLOR = 'gray'
TEXT_COLORS = ['black', 'blue', 'purple', 'violet']
INI_LEVEL_COLORS = ['red', 'orange', 'yellow', 'green', 'turquoise']


# 024-08-28
def load_colors():
    """ Loads colors from colors.ini into application constants. """
    global APP_BACKGROUND_COLOR, ENTRY_BACKGROUND_COLOR, TEXT_COLORS, INI_LEVEL_COLORS
    TEXT_COLORS.clear()
    INI_LEVEL_COLORS.clear()
    if os.path.isfile('./aesthetic/colors.ini'):
        with open('./aesthetic/colors.ini') as colors_buffer:
            colors_lines = colors_buffer.readlines()
        for line in colors_lines:
            if ' =' in line.strip():
                if ' = ' in line.strip():
                    color_key, value = line.strip().split(' = ')
                    if color_key == 'APP_BACKGROUND_COLOR':
                        APP_BACKGROUND_COLOR = value
                    elif color_key == 'ENTRY_BACKGROUND_COLOR':
                        ENTRY_BACKGROUND_COLOR = value
                    elif 'TEXT_COLOR' in color_key:
                        TEXT_COLORS.append(value)
                    elif 'LEVEL_COLOR' in color_key:
                        INI_LEVEL_COLORS.append(value)


def warning_file_save():
    """ Checks if the edited file have been edited since the previous saving and prompts a question if not. """
    global current_file_content_backup
    file_named = text_scope_select.get('1.0', 'end').replace('/', '\\').strip('\n\t {}')
    if file_named and current_file_content_backup:
        if text_file_content.get('1.0', 'end').strip() != current_file_content_backup.strip():
            save_file = tkinter.messagebox.askquestion(f'{PROGRAM_NAME}:', 'Do you want to save the file?')
            if save_file == 'yes':
                command_file_save()
    current_file_content_backup = ''


def on_app_close():
    """ Triggered on closing the application to catch unsaved changes in files. """
    set_log_update('closing application')
    warning_file_save()
    main_window.quit()


def clear_window():
    """ Cleans the screen of all containers. """
    global current_file_content_backup, current_window
    if current_window == 'file_editor':
        warning_file_save()
    current_window = ''
    retrieve(container_browser, container_modules, container_definition, container_find, container_replace,
             container_scope_select, container_file_content, container_settings)  # , container_select_file


def set_window_find():
    """ Loads the screen for finding text. """
    global key_to_command_current, current_window
    key_to_command_current = key_to_command_text.copy()
    clear_window()
    container_current.place_configure(height=UNIT_HEIGHT * 10)
    text_file_content.place_configure(height=UNIT_HEIGHT * 5)
    container_command.place_configure(height=UNIT_HEIGHT * 5)
    container_command_buttons.place_configure(y=UNIT_HEIGHT * 5)
    text_result.place_configure(height=UNIT_HEIGHT * 4)
    position(container_file_content, container_scope_select, container_find, button_function_replace,
             button_scope_select_folder, button_scope_except_file)
    container_file_content.place_configure(height=UNIT_HEIGHT * 5)
    container_scope_select.place_configure(y=int(UNIT_HEIGHT * 5.5))
    button_menu_back.config(command=set_window_file)
    button_menu_modules.configure(text='return to modules'.upper())
    retrieve(button_menu_settings, button_function_find)
    try:
        selection = convert_string(text_file_content.selection_get(), direction='display')
        text_find.delete('1.0', 'end')
        text_find.insert('1.0', selection)
    except UnboundLocalError:
        print('set_window_find error: UnboundLocalError')
    except _tkinter.TclError:
        print('set_window_find warning: no text selected')
    button_run.configure(text='find text'.upper(), command=command_run_find)
    button_execute.configure(text='clear logs'.upper(), command=set_log_update)
    text_result.focus()
    current_window = 'text_find'
    set_log_update('find feature loaded')
    command_run_find()


def set_window_replace():
    """ Loads the screen for replacing text. """
    global key_to_command_current, current_window
    key_to_command_current = key_to_command_text.copy()
    clear_window()
    text_file_content.place_configure(height=UNIT_HEIGHT * 5)
    container_current.place_configure(height=UNIT_HEIGHT * 11)
    container_command.place_configure(height=UNIT_HEIGHT * 4)
    container_command_buttons.place_configure(y=UNIT_HEIGHT * 4)
    text_result.place_configure(height=UNIT_HEIGHT * 3)
    position(container_file_content, container_scope_select, container_find, container_replace,
             button_function_find, button_scope_select_folder, button_scope_except_file)
    container_file_content.place_configure(height=UNIT_HEIGHT * 5)
    container_scope_select.place_configure(y=int(UNIT_HEIGHT * 5.5))
    retrieve(button_menu_settings, button_function_replace)
    try:
        selection = convert_string(text_file_content.selection_get(), direction='display')
        text_find.delete('1.0', 'end')
        text_find.insert('1.0', selection)
    except UnboundLocalError:
        print('set_window_find error: UnboundLocalError')
    except _tkinter.TclError:
        print('set_window_find warning: no text selected')
    button_menu_back.config(command=set_window_file)
    button_menu_modules.configure(text='return to modules'.upper())
    button_run.configure(text='replace text'.upper(), command=command_run_replace)
    button_run.focus()
    button_execute.configure(text='clear logs'.upper(), command=set_log_update)
    current_window = 'text_replace'
    set_log_update('replace feature loaded')


def set_window_move():
    """ Loads the screen for moving files. """
    global key_to_command_current, current_path, current_window
    key_to_command_current = key_to_command_text.copy()
    clear_window()
    container_current.place_configure(height=UNIT_HEIGHT * 5)
    container_command.place_configure(height=UNIT_HEIGHT * 10)
    container_command_buttons.place_configure(y=UNIT_HEIGHT * 10)
    text_result.place_configure(height=UNIT_HEIGHT * 9)
    position(container_scope_select)  # , container_folder_select
    try:
        current_path = f"{label_browser.cget('text')}/{listbox_browser.selection_get()}".replace('\\', '/')
    except _tkinter.TclError:
        print('file not selected')
    button_menu_back.configure(command=command_browser_back)
    label_scope_select.configure(text='file')
    text_scope_select.delete('1.0', 'end')
    try:
        text_scope_select.insert('1.0', f"{label_browser.cget('text')}/{listbox_browser.selection_get()}")
    except _tkinter.TclError:
        text_scope_select.insert('end', current_path)
    label_scope_except.configure(text='to folder')
    retrieve(button_scope_select_folder, button_scope_except_file)
    button_run.configure(text='move the file'.upper(), command=command_run_move)
    button_run.focus()
    button_execute.configure(text='clear logs'.upper(), command=set_log_update)
    current_window = 'file_move'
    set_log_update(f'move feature loaded. file: {current_path}')


def set_window_file():
    """ Loads the screen for file edition """
    global key_to_command_current, current_window
    if command_file_load():
        clear_window()
        key_to_command_current = key_to_command_text.copy()
        container_current.place_configure(height=UNIT_HEIGHT * 13)
        text_file_content.place_configure(height=UNIT_HEIGHT * 12)
        container_command.place_configure(height=UNIT_HEIGHT * 2)
        container_command_buttons.place_configure(y=UNIT_HEIGHT * 2)
        text_result.place_configure(height=int(UNIT_HEIGHT*0.75))
        position(container_file_content, button_run, button_function_find, button_function_replace)
        retrieve(button_execute)
        text_file_content.focus()
        button_menu_back.configure(command=command_browser_back)
        button_run.configure(text='save file'.upper(), command=command_file_save, state='normal')
        # button_execute.configure(text='reload file'.upper(), command=command_file_load)
        current_window = 'file_editor'
        set_log_update(f'file editor loaded. file {current_path}')
        return True
    else:
        return False


def set_window_modules():
    """ Loads the screen for managing modules. """
    global key_to_command_current, current_window
    key_to_command_current = key_to_command_module.copy()
    clear_window()
    container_current.place_configure(height=UNIT_HEIGHT * 13)
    position(container_modules, button_module_new, container_command, button_run, button_execute,
             button_menu_settings, container_command_buttons, text_result)  #
    # text_result.place_configure(height=UNIT_HEIGHT * 1)
    button_run.configure(text='take snapshot'.upper(), command=command_snapshot_take)
    button_execute.configure(text='compare snapshots'.upper(), command=command_snapshot_compare)
    button_menu_settings.configure(text='edit settings'.upper(), command=set_window_settings)
    button_menu_modules.configure(text='refresh modules'.upper())
    retrieve(button_module_copy, button_definition_edit, button_function_find, button_function_replace,
             button_menu_back)
    refresh_definitions()
    treeview_modules_idle.focus_set()
    try:
        treeview_modules_idle.selection_set(treeview_modules_idle.get_children()[0])
        treeview_modules_idle.focus(treeview_modules_idle.get_children()[0])
    except IndexError:
        pass
    current_window = 'modules'
    set_log_update('module manager window loaded.')


def set_window_definition():
    """ Loads the screen for modification of module definitions. """
    global key_to_command_current, current_window, global_modules
    if not global_modules:
        global_modules = modules_filter(return_type='definitions')
    key_to_command_current = key_to_command_text.copy()
    clear_window()
    position(container_definition, button_menu_back)
    retrieve(button_menu_settings, button_menu_back, button_execute)
    button_menu_back.configure(command=set_window_modules)
    button_run.configure(text='save parameters'.upper(), command=command_definition_save)
    button_menu_modules.configure(text='return to modules'.upper())
    module_selected = current_path.split('/')[-1]
    for module in global_modules:
        if module_selected == module['name']:
            level = 0
            for param in DEFINITION_EXAMPLE:
                if param == 'comment':
                    continue
                elif param == 'changes':
                    # TODO later: reformat the changes into a listbox
                    continue
                list_text_definition_editor[level].configure(state='normal')
                list_text_definition_editor[level].delete('1.0', 'end')
                if isinstance(module[param], bool):
                    list_text_definition_editor[level].insert('end', str(module[param]))
                else:
                    list_text_definition_editor[level].insert('end', module[param])
                if 'active' in param or param == 'path':  # or param == 'class':
                    list_text_definition_editor[level].configure(state='disabled')
                level += 1
    set_log_update('module definition edition feature loaded.')
    current_window = 'definition'


def set_window_browser():
    """ Loads the screen for browsing in modules directories. """
    global key_to_command_current, current_window
    key_to_command_current = key_to_command_browser.copy()
    clear_window()
    container_current.place_configure(height=UNIT_HEIGHT * 13)
    container_command.place_configure(height=UNIT_HEIGHT * 2)
    container_command_buttons.place_configure(y=UNIT_HEIGHT * 2)
    text_result.place_configure(height=int(UNIT_HEIGHT*0.75))
    position(container_browser)
    retrieve(button_module_new, button_function_find, button_function_replace, button_menu_settings)
    button_run.configure(text='open'.upper(), command=command_browser_forward)
    button_execute.configure(text='move file'.upper(), command=set_window_move)
    open_browser_item()
    button_menu_back.config(command=command_browser_back)
    listbox_browser.focus()
    current_window = 'browser'
    set_log_update(f'File browser loaded. Path: {os.path.abspath(current_path)}')


def set_window_settings():
    """ Loads the screen for settings edition. """
    global key_to_command_current, current_window
    key_to_command_current = key_to_command_text.copy()
    clear_window()
    position(container_settings, text_result)
    command_settings_reload()
    button_menu_settings.configure(text='save settings'.upper(), command=command_settings_save)
    button_menu_modules.configure(text='return to modules'.upper())
    retrieve(button_run, button_execute, button_function_find, button_function_replace)
    current_window = 'settings'
    set_log_update('settings edition feature loaded')


def command_snapshot_take():
    """ Takes a snapshot of all files in the selected directory. """
    set_log_update('generating snapshot - please wait')
    try:
        result_path = snapshot_take()
    except InternalError:
        set_log_update(f'snapshot not generated. path not selected')
    else:
        set_log_update(f'snapshot generated. path: {result_path}')


def command_snapshot_compare():
    """ Runs a comparison between selected snapshots. """
    set_log_update('generating snapshot comparison - please wait')
    try:
        result_path = snapshot_compare(return_type='path')
    except InternalError:
        set_log_update(f'snapshot comparison not generated. Snapshots not selected.')
    else:
        set_log_update(f'snapshot comparison generated. path: {result_path}')


def command_settings_save():
    """ Reads the values inserted in the settings text fields and saves them to the SETTINGS_FILE. """
    counter = 0
    setting_value = []
    new_settings = {}
    for entry_setting in list_entry_settings:
        setting_value.append(entry_setting.get())
    for setting_key in settings:
        if setting_key == 'comment':
            continue
        if settings[setting_key] != setting_value[counter]:
            # TODO later: check for empty settings list
            if isinstance(settings[setting_key], list):
                # for setting_container_index in range(len(setting_value[counter].split(', '))):
                setting_dict_list = setting_value[counter].split(', ')
                if settings[setting_key] and setting_dict_list:
                    if settings[setting_key] != setting_dict_list:
                        new_settings[setting_key] = setting_dict_list
                elif setting_dict_list != ['']:
                    new_settings[setting_key] = setting_dict_list
                else:
                    pass
            elif isinstance(settings[setting_key], str):
                new_settings[setting_key] = setting_value[counter]
        counter += 1
    if new_settings:
        try:
            output = settings_save_to_file(new_settings)
            set_log_update(output)
        except InternalError as error:
            set_log_update(error.message)
            command_settings_reload()


def command_settings_reload():
    """ Reads the settings from the SETTINGS_FILE and inserts them into the settings text fields. """
    global settings
    settings = settings_read()
    counter = 0
    for setting_key in settings:
        if setting_key == 'comment':
            continue
        list_entry_settings[counter].delete('0', 'end')
        if isinstance(settings[setting_key], list):
            list_entry_settings[counter].insert('end', ', '.join(settings[setting_key]))
        else:
            list_entry_settings[counter].insert('end', settings[setting_key])
        counter += 1


def command_select_folder(text_widget):
    """ Launches a window for selecting a folder and pastes it into the folder text field. """
    selected_folder = askdirectory(
        title=f'{PROGRAM_NAME}: select a folder',
        initialdir=current_path if os.path.isdir(current_path) else current_path[:current_path.rfind('/')])
    # text_select_folder.delete('1.0', 'end')
    if len(text_widget.get('1.0', 'end')) > 1:
        text_widget.insert('end', f', {selected_folder}')
    else:
        text_widget.insert('end', selected_folder)
    set_log_update(f'folder {selected_folder} selected')


def command_select_file(text_widget):
    """ Launches a window for selecting one or more file(s) and pastes it into the file text field. """
    selected_files = askopenfilenames(
        title=f'{PROGRAM_NAME}: select one or multiple files',
        initialdir=current_path if os.path.isdir(current_path) else current_path[:current_path.rfind('/')])
    if selected_files:
        # text_select_file.delete('1.0', 'end')
        strip_chars = "(),'"
        if len(text_widget.get('1.0', 'end')) > 1:
            text_widget.insert('end', f', {str(selected_files).strip(strip_chars)}')
        else:
            text_widget.insert('end', f"{str(selected_files).strip(strip_chars)}")
    set_log_update(f'file(s) {selected_files} selected')


def set_text_color(event=None):
    """ Provides colors to elements of an edited text file that are defined as its delimiters. """
    if event:
        pass
    for tag_name in text_file_content.tag_names():
        text_file_content.tag_delete(tag_name)
    text_lines = text_file_content.get('1.0', 'end').split('\n')
    for line_index in range(1, len(text_lines) + 1):
        line = text_lines[line_index - 1]
        rest_of_line = line
        if line.strip() == '':
            continue
        elif line.strip()[0] in INI_COMMENTS:
            text_file_content.tag_add('comment', f'{line_index}.0', f'{line_index}.end')
            rest_of_line = ''
        elif INI_COMMENTS[0] in line:
            text_file_content.tag_add('comment', f'{line_index}.{line.index(INI_COMMENTS[0])}', f'{line_index}.end')
            rest_of_line = line[:line.index(INI_COMMENTS[0])]
        elif INI_COMMENTS[1]*2 in line:
            text_file_content.tag_add('comment', f'{line_index}.{line.index(INI_COMMENTS[1]*2)}', f'{line_index}.end')
            rest_of_line = line[:line.index(INI_COMMENTS[1]*2)]
        text_file_content.tag_config('comment', foreground='grey')
        if rest_of_line:
            level = rest_of_line.rstrip().count(LEVEL_INDENT)
            text_file_content.tag_config(f'level{level}', foreground=INI_LEVEL_COLORS[level])
            if rest_of_line.split()[0].strip() in current_levels[level]:
                text_file_content.tag_add(f'level{level}', f'{line_index}.0',
                                          f'{line_index}.{len(rest_of_line)}')
            elif rest_of_line.strip() in INI_ENDS:
                text_file_content.tag_add(f'level{level}', f'{line_index}.0',
                                          f'{line_index}.{len(rest_of_line)}')
    # return True


def command_text_comment():
    """ Comments the text selected in the text editor """
    text_to_comment = ''
    try:
        text_to_comment += text_file_content.get('insert linestart', 'sel.last lineend')
    except _tkinter.TclError:
        text_to_comment += text_file_content.get('insert linestart', 'insert lineend')
        text_file_content.tag_add('sel', 'insert linestart', 'insert lineend')
    lines_to_comment = text_to_comment.split('\n')
    text_commented = ''
    for line in lines_to_comment:
        for level in range(7):
            if line.startswith(LEVEL_INDENT * (6 - level)):
                text_commented += f'{LEVEL_INDENT * (6 - level)}; {line.strip()}\n'
                break
    if text_commented:
        text_file_content.replace('sel.first linestart', 'sel.last lineend + 1 chars', text_commented)
    set_text_color()
    set_log_update('selected text has been commented out')


def command_text_uncomment():
    """ Uncomments the text selected in the text editor """
    text_to_comment = ''
    try:
        text_to_comment += text_file_content.get('insert linestart', 'sel.last lineend')
    except _tkinter.TclError:
        text_file_content.tag_add('sel', 'insert linestart', 'insert lineend')
        text_to_comment += text_file_content.get('insert linestart', 'insert lineend')
    lines_to_comment = text_to_comment.split('\n')
    text_commented = ''
    for line in lines_to_comment:
        for level in range(7):
            if line.startswith(LEVEL_INDENT * (6 - level)):
                if '; ' in line:
                    text_commented += f"{LEVEL_INDENT * (6 - level)}{line.strip()[len('; '):]}\n"
                elif '//' in line:
                    text_commented += f"{LEVEL_INDENT * (6 - level)}{line.strip()[len('//'):]}\n"
                break
    if text_commented:
        text_file_content.replace('sel.first linestart', 'sel.last lineend + 1 chars', text_commented)
    set_text_color()
    set_log_update('selected text has been uncommented')


def command_file_load():  # not a command anymore
    """
    Loads the selected file into the text editor and into a variable.
    :return: True if the file is readable | False if the file could not be read
    """
    global current_levels, current_file_content_backup, current_path
    # warning_file_save()
    text_file_content.delete('1.0', 'end')
    file_loaded = text_scope_select.get('1.0', 'end').replace('\\', '/').strip('\n\t {}')
    current_path = file_loaded
    try:
        current_file_content_backup, current_levels = load_file(full_path=file_loaded)
        text_file_content.insert('end', current_file_content_backup)
        set_text_color()
        set_log_update(f'file {file_loaded} loaded successfully')
        return True
    except TypeError:
        command_browser_back()
        set_log_update('cannot open this type of file')
    except InternalError as error:
        command_browser_back()
        set_log_update(error.message)
    return False


def command_file_save():
    """ Saves the text edited in the application back into its original file. """
    content_to_save = text_file_content.get('1.0', 'end')
    file_named = text_scope_select.get('1.0', 'end').replace('/', '\\').strip().replace('{', '').replace('}', '')
    with open(file_named, 'w') as file_overwritten:
        file_overwritten.write(content_to_save)
    set_log_update(f'file {file_named} saved')


def command_copy_find():
    """ Copies the string to find into the field of the string to replace it with. """
    find = text_find.get('1.0', 'end').strip()
    text_replace.delete('1.0', 'end')
    text_replace.insert('1.0', find)


def command_run_find():
    """ Runs the find_text function. """
    find = convert_string(text_find.get('1.0', 'end').strip(), direction='display')
    scope = text_scope_select.get('1.0', 'end').replace('/', '\\').strip()
    exception_string = text_scope_except.get('1.0', 'end').replace('/', '\\').strip()
    exceptions = exception_string.split(', ')
    if find and scope:
        output = find_replace_text(find=find, scope=scope, exceptions=exceptions, mode='initiate')
        set_log_update(output)


def command_run_replace():
    """ Runs the replace_text function. """
    find = convert_string(text_find.get('1.0', 'end').strip(), direction='display')
    replace_with = convert_string(text_replace.get('1.0', 'end').strip(), direction='display')
    scope = text_scope_select.get('1.0', 'end').replace('/', '\\').strip()
    exception_string = text_scope_except.get('1.0', 'end').replace('/', '\\').strip()
    # if ', ' in exception_string:
    exceptions = exception_string.split(', ')
    output = find_replace_text(find=find, replace_with=replace_with, scope=scope, exceptions=exceptions)
    set_log_update(output)
    text_file_content.delete('1.0', 'end')
    text_file_content.insert('end', load_file(scope)[0])
    set_text_color()


def command_run_move():
    """ Runs the move_file function. """
    files_named = text_scope_select.get('1.0', 'end').replace('\\', '/').strip()
    to_folder = text_scope_except.get('1.0', 'end').replace('\\', '/').strip()
    output = ''
    for file_named in files_named.split('} {'):
        file_named = file_named.replace('{', '').replace('}', '')
        try:
            output += move_file(file_named, to_folder)
        except InternalError as error:
            output += error.message
        else:
            module_index_start = current_path.find(current(MODULES_LIBRARY)) + len(current(MODULES_LIBRARY)) + 1
            module_index_end = current_path.replace('\\', '/').find('/', module_index_start)
            current_module_name = current_path[module_index_start: module_index_end]
            current_module_list = modules_filter(name=current_module_name)
            if current_module_list:
                current_module = current_module_list[0]
            else:
                module_index_start = current_path.find(current(INSTALL_PATH)) + len(current(INSTALL_PATH)) + 1
                module_index_end = current_path.replace('\\', '/').find('/', module_index_start)
                current_module_name = current_path[module_index_start: module_index_end]
                current_module_list = modules_filter(name=current_module_name)
                if current_module_list:
                    current_module = current_module_list[0]
                else:
                    output += '\nmodule not found - definition not updated.\n'
                    return set_log_update(output)
            new_changes = {}
            for file_path in current_module['changes']:
                file_name = file_named.replace('\\', '/').split('/')[-1]
                if file_path.split('/')[-1] == file_name:
                    file_rel_path = '..' + to_folder[module_index_end + 1:].replace('\\', '/')
                    new_changes[f'{file_rel_path}/{file_name}'] = current_module['changes'][file_path]
                else:
                    new_changes[file_path] = current_module['changes'][file_path]
            definition_edit(current_module, changes=new_changes)
    set_log_update(output)


def command_run_duplicate():
    """ Runs the duplicates_commenter function. """
    file_named = text_scope_select.get('1.0', 'end').replace('/', '\\').strip()
    output = duplicates_commenter(in_file=file_named)
    set_log_update(output)


def command_definition_save():
    """ Saves the current module definition. """
    output = 'module data edition failed'
    module_selected = current_path.split('/')[-1]
    for module in global_modules:
        if module_selected == module['name']:
            edited_parameters = {}
            expected_definition = module.copy()
            level = 0
            for param in DEFINITION_EXAMPLE:
                if param == 'comment':
                    continue
                elif param == 'changes':
                    # TODO later: reformat the changes
                    continue
                value = list_text_definition_editor[level].get('1.0', 'end').strip()
                if value != module[param]:
                    if param == 'class' and value not in DEFINITION_CLASSES:
                        break
                    elif param != 'active':
                        edited_parameters[param] = value
                        expected_definition[param] = value
                level += 1
            try:
                new_definition = definition_edit(module, **edited_parameters)
                if new_definition == expected_definition:
                    output = 'new definition saved'
                if 'class' in edited_parameters and module['active'] is True:
                    module.reload_after_class_change()
                break
            except InternalError as error:
                output = error.message
    set_log_update(output)


def on_select_module_idle(event):
    """ Triggered on selection of a non-active module, shows or hides the desired buttons"""
    global current_path, key_to_command_current
    if event:
        pass
    try:
        current_path = (f"{current(MODULES_LIBRARY)}/"
                        f"{treeview_modules_idle.item(treeview_modules_idle.selection()[0], 'values')[0]}")
        treeview_modules_active.selection_remove(treeview_modules_active.selection()[0])
        # selection_remove is a selection event steeling focus to the other list
        treeview_modules_idle.selection_set(treeview_modules_idle.selection()[0])
    except IndexError:
        pass
    key_to_command_current['<Return>'] = command_module_browse
    position(button_module_attach, button_module_browse, button_definition_edit)  # , button_module_copy
    retrieve(button_module_retrieve, button_module_reload)
    treeview_modules_idle.focus()


def on_select_module_active(event):
    """ Triggered on selection of an active module, shows or hides the desired buttons. """
    global current_path, key_to_command_current
    if event:
        pass
    try:
        current_path = (f"{current(MODULES_LIBRARY)}/"
                        f"{treeview_modules_active.item(treeview_modules_active.selection()[0], 'values')[0]}")
        treeview_modules_idle.selection_remove(treeview_modules_idle.selection()[0])
        treeview_modules_active.selection_set(treeview_modules_active.selection()[0])
    except IndexError:
        pass
    key_to_command_current['<Return>'] = command_module_browse
    position(button_module_retrieve, button_module_reload, button_module_browse, button_definition_edit)
    retrieve(button_module_attach)


def refresh_definitions():
    """ Refreshes the lists of active and non-active modules. """
    # set_log_update('refreshing definitions...')
    global global_modules
    try:
        set_log_update(detect_new_modules())
        treeview_modules_active.delete(*treeview_modules_active.get_children())
        treeview_modules_idle.delete(*treeview_modules_idle.get_children())
        active_modules = modules_filter('definitions', active=True)
        active_module_parent_dict = modules_sort(modules=active_modules)
        for module in active_modules:
            treeview_modules_active.insert(
                parent='', index=active_modules.index(module), iid=active_modules.index(module),
                values=tuple(module[_] for _ in MODULE_COLUMNS)
            )
            global_modules.append(module)
        for module in active_modules:
            try:
                parent_index = active_module_parent_dict[module['name']]
                treeview_modules_active.move(active_modules.index(module), parent_index, 0)
            except KeyError:
                pass
        treeview_modules_active.open_children()
        idle_modules = modules_filter('definitions', active=False)
        idle_module_parent_dict = modules_sort(modules=idle_modules)
        for module in idle_modules:
            treeview_modules_idle.insert(
                parent='', index=idle_modules.index(module), iid=idle_modules.index(module),
                values=tuple(module[_] for _ in MODULE_COLUMNS)
            )
            global_modules.append(module)
        for module in idle_modules:
            try:
                parent_index = idle_module_parent_dict[module['name']]
                treeview_modules_idle.move(idle_modules.index(module), parent_index, 0)
            except KeyError:
                pass
        treeview_modules_idle.open_children()
    except InternalError:
        set_log_update('definitions not loaded - settings not loaded.')
        return
    retrieve(button_module_retrieve, button_module_attach)


def command_module_new():
    """ Creates a new module after asking for a name and a way to create it. """
    global new_module_name
    NewModuleDialog()
    if new_module_name:
        set_log_update(f'command_module_new: creating module {new_module_name}. Please wait ...')
        set_log_update(module_copy(new_module_name, changes_source=new_module_source))
        # snapshot_take([])
        refresh_definitions()
    else:
        set_log_update('command_module_new error: a correct unique name was not provided')
    new_module_name = ''


def command_module_copy():
    """ Copies the selected module. Currently, not in use """
    module_selected = current_path
    name = module_selected.split('/')[-1] + '_copy'
    set_log_update(module_copy(name, module_selected))
    refresh_definitions()


def command_module_attach():
    # TODO: if the module overrides another, ask if save it as ancestor / heir
    """ Activates the selected module """
    global global_modules
    if not global_modules:
        global_modules = modules_filter(return_type='definitions')
    try:
        module_selected = treeview_modules_idle.item(treeview_modules_idle.focus(), 'values')[0]
        set_log_update(f'loading module {module_selected} ...')
        for module in global_modules:
            if module['name'] == module_selected:
                module.attach()
                set_log_update(f'module {module_selected} loaded')
                return refresh_definitions()
        set_log_update(f'command_module_attach error: module {module_selected} not found')
    except _tkinter.TclError:
        set_log_update('command_module_attach warning: TclError')
    except InternalError as err:
        set_log_update(err.message)


def command_module_retrieve():
    """ Deactivates the selected module. """
    global global_modules
    if not global_modules:
        global_modules = modules_filter(return_type='definitions')
    try:
        module_selected = treeview_modules_active.item(treeview_modules_active.focus(), 'values')[0]
        set_log_update(f'unloading mod {module_selected} ...')
        for module in global_modules:
            if module['name'] == module_selected:
                changes = module_detect_changes(module_directory=f"{current(MODULES_LIBRARY)}/{module['name']}")
                # TODO: test changes
                if changes:
                    do_proceed = tkinter.messagebox.askokcancel(
                        title=f'{PROGRAM_NAME}: module retrieval:',
                        message='Files have been changed since the module have been attached.\n'
                                f'They will be deleted if the module is a {DEFINITION_CLASSES[1]}'
                                f' or incorporated if it is a {DEFINITION_CLASSES[0]}'
                                ' Do you wish to proceed?\n'
                                f'{changes}'
                    )
                    if do_proceed is True:
                        changes = ''
                if not changes:
                    module.retrieve()
                    refresh_definitions()
                    set_log_update(f"module {module['name']} deactivated")
                    return
                else:
                    set_log_update(f'command_module_retrieve error: module {module_selected} retrieval aborted')
        set_log_update(f'command_module_retrieve error: module {module_selected} not found')
    except _tkinter.TclError:
        set_log_update('command_module_retrieve error: module not selected')
    except InternalError as err:
        set_log_update(err.message)


def command_module_reload():
    """ Reloads the selected module by detaching it and attaching again. """
    global global_modules
    if not global_modules:
        global_modules = modules_filter(return_type='definitions')
    try:
        module_selected = treeview_modules_active.item(treeview_modules_active.focus(), 'values')[0]
        set_log_update(f'Reloading module {module_selected}. Please wait ...')
        for module in global_modules:
            if module['name'] == module_selected:
                if module.reload():
                    refresh_definitions()
                    set_log_update(f'Module {module_selected} reloaded. Please wait ...')
                    return
                else:
                    set_log_update(f'The module could not be reloaded.')
        set_log_update(f'command_module_reload error: mod {module_selected} not found')
    except _tkinter.TclError:
        set_log_update('command_module_reload error: no mod selected')


def command_module_browse(event=None):
    """ Allows to start browsing from the object folder if it can be found. """
    global current_path
    if event:
        pass
    current_module = modules_filter(name=current_path.split('/')[-1])[0]
    game_paths = game_names()
    if current_module['class'] == DEFINITION_CLASSES[0] and current_module['active']:
        if not current_module['game']:
            for change_key in current_module['changes']:
                # if os.path.isdir(change_key.split('/')[0]):
                #     current_path = change_key.split('/')[0]
                change_split = change_key.split('/')
                if os.path.isdir('/'.join(change_split[:2])) and '/'.join(change_split[1:-1]) in game_paths:
                    current_path = '/'.join((change_split[0], game_paths[game_paths.index(change_split[1])]))
                    if os.path.isdir(f'{current_path}/data/ini/object'):
                        current_path = f'{current_path}/data/ini/object'
                    break
        elif current_module['game'] in game_paths:
            if os.path.isdir(f"../{game_paths[game_paths.index(current_module['game'])]}"):
                current_path = f"../{game_paths[game_paths.index(current_module['game'])]}"
        elif f"{current_module['game']}/aotr" in game_paths:
            if os.path.isdir(f"../{current_module['game']}/aotr/data/ini/object"):
                current_path = f"../{current_module['game']}/aotr/data/ini/object"
            elif os.path.isdir(f"../{current_module['game']}/aotr"):
                current_path = f"../{current_module['game']}/aotr"
        # else:
        #     for game_name in game_paths:
        #         if os.path.isdir(f'../{game_name}/data/ini/object'):
        #             current_path = f'../{game_name}/data/ini/object'
        #             break
        #         # elif os.path.isdir(f'../{game_name}'):
        #         #     current_path = f'../{game_name}'
        #         #     break
    else:
        for game_name in game_paths:
            if os.path.isdir(f'{current_path}/{game_name}/data/ini/object'):
                current_path = f'{current_path}/{game_name}/data/ini/object'
                break
            elif os.path.isdir(f'{current_path}/{game_name}'):
                current_path = f'{current_path}/{game_name}'
                break
    button_menu_modules.configure(text='return to modules'.upper())
    set_window_browser()


def command_browser_back():
    """ Browses back a level in the directory hierarchy or returns to browser from file screen. """
    global current_path, key_to_command_current
    # if current_window == 'file_editor':
    #     warning_file_save()
    if current_window == 'text_find' or current_window == 'text_replace':
        set_window_file()
    # if len(current_path) > len(current(MODULES_LIBRARY)):
    if os.path.isdir(current_path[:current_path.rfind('/')]):
        current_path = current_path[:current_path.rfind('/')]
        if main_window.focus_get() == listbox_browser:
            open_browser_item()
        else:
            set_window_browser()
    # if len(current_path) <= len(current(MODULES_LIBRARY)):
    if len(current_path) <= len('..'):
        retrieve(button_menu_back)
        key_to_command_current['<BackSpace>'] = set_window_modules
    set_log_update(f'going back to {os.path.abspath(current_path)}')
    key_to_command_current = key_to_command_browser.copy()


def on_select_browser_item(event=None):
    """ Triggered on selection of an item in the directory to enable or disable buttons. """
    global key_to_command_current
    if event:
        pass
    if current_window != 'file_editor':
        try:
            file_name = listbox_browser.selection_get()
            if file_name == DEFINITION_NAME or file_name.endswith('.big'):
                raise InternalError
            elif os.path.isfile(f'{current_path}/{listbox_browser.selection_get()}'):
                key_to_command_current = key_to_command_browser.copy()
                button_run.configure(text='open file'.upper())
                position(button_run, button_execute)  # , button_function_duplicate
            else:
                raise IndexError
        except IndexError:
            position(button_run)
            button_run.configure(text='open folder'.upper())
            retrieve(button_execute)
        except InternalError:
            retrieve(button_run, button_execute)
            try:
                key_to_command_current.pop('<Return>')
            except KeyError:
                pass


def command_browser_forward(event=None):
    """ Gets the selected item in the directory and opens it """
    global current_path
    if event:
        pass
    try:
        item_selected = listbox_browser.get(listbox_browser.curselection())
        current_path += f'/{item_selected}'
        if os.path.isdir(current_path):
            os.listdir(current_path)
        set_log_update(f'going to {os.path.abspath(current_path)}')
        open_browser_item()
    except _tkinter.TclError:
        print('command_browser_forward error: _tkinter.TclError - no selection')
    except PermissionError as error:
        set_log_update(error.strerror)
        current_path = current_path[:current_path.rfind('/')]


def open_browser_item():
    """ Opens the selected item in the directory whether it is a folder or a file. """
    if os.path.isdir(current_path):
        try:
            output_folders, output_files = load_directories(current_path)
            listbox_browser.delete(0, 'end')
            item_index = 0
            for output_folder in output_folders:
                listbox_browser.insert(item_index, output_folder)
                listbox_browser.itemconfig(item_index, foreground=INI_LEVEL_COLORS[1])
                item_index += 1
            for output_file in output_files:
                listbox_browser.insert(item_index, output_file)
                listbox_browser.itemconfig(
                    item_index,
                    foreground=INI_LEVEL_COLORS[3] if output_file.endswith('.ini') else INI_LEVEL_COLORS[2]
                )
                item_index += 1
            listbox_browser.activate(0)
            if not output_folders and not output_files:
                retrieve(button_run, button_execute)
            elif not output_folders:
                button_run.configure(text='open file'.upper())
                position(button_execute)
            else:
                button_run.configure(text='open folder'.upper())
                retrieve(button_execute)
            listbox_browser.select_set(0)
            set_log_update(f'opened {os.path.abspath(current_path)}')
        except InternalError as error:
            set_log_update(error.message)
    elif os.path.isfile(current_path):
        text_scope_select.delete('1.0', 'end')
        text_scope_select.insert('end', current_path)
        if set_window_file():
            # command_file_load()
            listbox_browser.selection_clear(listbox_browser.curselection())
            position(button_execute)
            set_log_update(f'opened {os.path.abspath(current_path)}')
    label_browser.configure(text=os.path.abspath(current_path))
    position(button_menu_back)


def focus_on_next_item():
    """ Binds arrow pressing with the change between the lists of active and non-active modules. """
    if main_window.focus_get() == treeview_modules_idle:
        treeview_modules_idle.selection_remove(treeview_modules_idle.selection())
        treeview_modules_active.focus_set()
        if treeview_modules_active.focus():
            module_selected = treeview_modules_active.focus()
        elif treeview_modules_active.selection():
            module_selected = treeview_modules_active.selection()
        elif len(treeview_modules_active.get_children()) > 0:
            module_selected = treeview_modules_active.get_children()[0]
        else:
            return
        treeview_modules_active.selection_set(module_selected)
    elif main_window.focus_get() == treeview_modules_active:
        treeview_modules_active.selection_remove(treeview_modules_active.selection())
        treeview_modules_idle.focus_set()
        treeview_modules_idle.selection_set(treeview_modules_idle.focus())
        if treeview_modules_idle.focus():
            module_selected = treeview_modules_idle.focus()
        elif treeview_modules_idle.selection():
            module_selected = treeview_modules_idle.selection()
        elif treeview_modules_idle.get_children():
            module_selected = treeview_modules_idle.get_children()[0]
        else:
            return
        treeview_modules_idle.selection_set(module_selected)
    elif main_window.focus_get() == listbox_browser:
        list_length = len(listbox_browser.get('0', 'end'))
        selected_item_index = listbox_browser.get('0', 'end').index(listbox_browser.selection_get())
        listbox_browser.selection_set((selected_item_index + 1) % list_length)
    else:
        print(main_window.focus_get())


def set_log_update(line=''):
    """ Replaces the content of the result field with a given content. """
    text_result.configure(state='normal')
    text_result.delete('1.0', 'end')
    text_result.insert('end', line)
    text_result.configure(state='disabled')
    main_window.update()


def use_selected_text(event=None):
    """ Binds key presses with functions in the file editor. """
    try:
        if event.keysym == 'f':
            set_window_find()
        elif event.keysym == 'r':
            set_window_replace()
        elif event.keysym == 'slash':
            command_text_comment()
        elif event.keysym == 'backslash':
            command_text_uncomment()
        else:
            print(event.keysym)
    except UnboundLocalError:
        print("error use_selected_text: selection seems empty")


def press_key_in_current_mode(event=None):
    """ Binds key presses to functions in the current dictionary of key-functions. """
    if f'<{event.keysym}>' in key_to_command_current:
        key_to_command_current[f'<{event.keysym}>']()
    else:
        # print(f'<{event.keysym}>')
        pass


def settings_select_new_directory(index_funct):
    """ Prompts to select a directory and replaces the old one with it in a settings entry field. """
    added = askdirectory(title=f'{PROGRAM_NAME}: select a new directory', initialdir='../')
    if added:
        list_entry_settings[index_funct].delete(0, 'end')
        if '/' == added[-1]:
            added = added[:-1]
        new_path = os.path.relpath(added).replace('\\', '/')
        list_entry_settings[index_funct].insert('end', new_path)
        set_log_update('setting configuration successful')
    else:
        set_log_update('setting configuration aborted')


def settings_select_add_directory(index_funct):
    """ Prompts to select a directory and adds it to a settings entry field. """
    present = list_entry_settings[index_funct].get()
    added = f"{askdirectory(title=f'{PROGRAM_NAME}: select a new directory', initialdir='../')}"
    if added:
        new_path = os.path.relpath(added).replace('\\', '/')
        if not present:
            list_entry_settings[index_funct].insert('end', new_path)
        else:
            list_entry_settings[index_funct].insert('end', f', {new_path}')
        set_log_update('setting configuration successful')
    else:
        set_log_update('setting configuration aborted')


def coordinate(**key_args):
    return key_args


# 024-08_06
def position(*elements):
    for element in elements:
        try:
            element.place(dict_position[element])
        except AttributeError as err:
            print(f'element {element} not predefined\n{err}')


def retrieve(*elements):
    for element in elements:
        try:
            element.place_forget()
        except NameError:
            print(element)


key_to_command_module = {
    '<Return>': command_browser_forward,
    '<Right>': focus_on_next_item,
    '<Left>': focus_on_next_item,
}
key_to_command_browser = {
    '<Return>': command_browser_forward,
    '<BackSpace>': command_browser_back,
    '<Escape>': set_window_modules,
}
key_to_command_text = {
    '<Escape>': command_browser_back
}
key_to_command_current = {
    '<Return>': set_window_modules,
}


load_colors()
initiate()
settings = settings_read()

main_window = tkinter.Tk()
main_window.iconbitmap('aesthetic/icon.ico')
main_window.title(PROGRAM_NAME)
main_window.minsize(width=1100, height=400)
main_window.maxsize(width=1600, height=900)
main_window.geometry('1250x650')
main_window.configure(padx=10, pady=10, background=APP_BACKGROUND_COLOR)
main_window.bind('<Key>', press_key_in_current_mode)
main_window.bind_all('<Control-Key-f>', use_selected_text)
main_window.bind_all('<Control-Key-r>', use_selected_text)
set_title_bar_color(main_window)

# TODO later: loading screen

container_command = tkinter.Frame(master=main_window)
container_command_buttons = tkinter.Frame(master=container_command)
button_run = tkinter.Button(master=container_command_buttons)
button_execute = tkinter.Button(master=container_command_buttons, text='clear logs'.upper(), command=set_log_update)
text_result = tkinter.Text(master=container_command, state='disabled')
button_menu_modules = tkinter.Button(
    master=container_command_buttons, text='modules'.upper(), command=set_window_modules)
button_menu_back = tkinter.Button(master=container_command_buttons, text='back'.upper())  # , state='disabled'
button_menu_settings = tkinter.Button(
    master=container_command_buttons, text='edit settings'.upper(), command=set_window_settings)

# button_function_duplicate = tkinter.Button(
#     master=container_command_buttons, text='remove duplicates'.upper(), command=set_window_duplicates)
button_function_find = tkinter.Button(
    master=container_command_buttons, text='find text'.upper(), command=set_window_find)
button_function_replace = tkinter.Button(
    master=container_command_buttons, text='replace text'.upper(), command=set_window_replace)

container_current = tkinter.Frame(master=main_window)

container_file_content = tkinter.Frame(master=container_current)
text_file_content = tkinter.Text(master=container_file_content, width=TEXT_WIDTH, height=30, undo=True)
numeration = TkLineNumbers(container_file_content, text_file_content, justify='right')
main_window.event_delete('<<SelectAll>>', '<Control-Key-/>')
text_file_content.bind('<Control-Key-/>', use_selected_text)
text_file_content.bind(r'<Control-Key-\>', use_selected_text)
text_file_content.bind('<<Modified>>', lambda event: main_window.after_idle(numeration.redraw), add=True)
text_file_content.bind('<<Modified>>', lambda event: main_window.after_idle(set_text_color), add=True)

container_settings = tkinter.Frame(master=container_current)
list_labels_settings = []
list_entry_settings = []
list_buttons_settings = []
for setting in settings:
    if setting == 'comment':
        continue
    list_labels_settings.append(tkinter.Label(master=container_settings, text=setting))
    list_entry_settings.append(tkinter.Entry(master=container_settings))
    list_buttons_settings.append(tkinter.Button(master=container_settings, text='select'.upper()))

try:
    # list_buttons_settings[0].configure(command=lambda: settings_select_new_directory(0))
    # list_buttons_settings[1].configure(command=lambda: settings_select_new_directory(1))
    list_buttons_settings[2].configure(command=lambda: settings_select_new_directory(2))
    list_buttons_settings[3].configure(command=lambda: settings_select_new_directory(3))
    list_buttons_settings[4].configure(command=lambda: settings_select_add_directory(4))
except IndexError:
    pass

container_modules = tkinter.Frame(master=container_current)
label_modules_idle = tkinter.Label(master=container_modules, text='available modules:')
treeview_modules_idle = ColumnedListbox(master=container_modules, width=LIST_WIDTH, height=10)
treeview_modules_idle.bind('<<TreeviewSelect>>', on_select_module_idle)
treeview_modules_idle.bind('<Double-1>', command_module_browse)
container_module_buttons = tkinter.Frame(master=container_modules, pady=7)
button_module_attach = tkinter.Button(
    master=container_module_buttons, text='attach module'.upper(), command=command_module_attach)
button_module_retrieve = tkinter.Button(
    master=container_module_buttons, text='detach module'.upper(), command=command_module_retrieve)
button_module_reload = tkinter.Button(
    master=container_module_buttons, text='reload module'.upper(), command=command_module_reload)
button_module_browse = tkinter.Button(
    master=container_module_buttons, text='open module'.upper(), command=command_module_browse)
button_module_copy = tkinter.Button(
    master=container_module_buttons, text='copy module'.upper(), command=command_module_copy)
button_module_new = tkinter.Button(
    master=container_module_buttons, text='new module'.upper(), command=command_module_new)
button_definition_edit = tkinter.Button(
    master=container_module_buttons, text='edit module data'.upper(), command=set_window_definition)

label_modules_active = tkinter.Label(master=container_modules, text='active modules:', width=UNIT_WIDTH * 2)
treeview_modules_active = ColumnedListbox(master=container_modules, width=LIST_WIDTH, height=10)
treeview_modules_active.bind('<<TreeviewSelect>>', on_select_module_active)
treeview_modules_active.bind('<Double-1>', command_module_browse)

container_definition = tkinter.Frame(master=container_current)
list_labels_module_editor = []
list_text_definition_editor = []
for key in DEFINITION_EXAMPLE:
    if key == 'comment' or key == 'changes':
        continue
    list_labels_module_editor.append(tkinter.Label(master=container_definition, text=key))
    list_text_definition_editor.append(tkinter.Text(master=container_definition))

container_browser = tkinter.Frame(master=container_current)
label_browser = tkinter.Label(master=container_browser)
listbox_browser = tkinter.Listbox(master=container_browser, width=LIST_WIDTH, height=20)
listbox_browser.bind('<<ListboxSelect>>', on_select_browser_item)
listbox_browser.bind('<Double-1>', command_browser_forward)

# container_select_file = tkinter.Frame(master=container_current)
# label_file_select = tkinter.Label(master=container_select_file, text='in file(s):')
# button_file_select = tkinter.Button(
#     master=container_select_file, text='select a file'.upper(), command=command_select_file)
# text_file_select = tkinter.Text(master=container_select_file, width=TEXT_WIDTH, height=3)

# container_folder_select = tkinter.Frame(master=container_current)
# label_folder_select = tkinter.Label(master=container_folder_select, text='in folder(s):')
# button_folder_select = tkinter.Button(
#     master=container_folder_select, text='select a folder'.upper(), command=command_select_folder)
# text_folder_select = tkinter.Text(master=container_folder_select, height=3)

container_scope_select = tkinter.Frame(master=container_current)
label_scope_select = tkinter.Label(master=container_scope_select, text='in file(s) or folder(s):')
text_scope_select = tkinter.Text(master=container_scope_select)
button_scope_select_file = tkinter.Button(
    master=container_scope_select, text='select a file'.upper(), command=lambda: command_select_file(text_scope_select))
button_scope_select_folder = tkinter.Button(
    master=container_scope_select, text='select a folder'.upper(),
    command=lambda: command_select_folder(text_scope_select))
label_scope_except = tkinter.Label(master=container_scope_select, text='except:')
text_scope_except = tkinter.Text(master=container_scope_select)
button_scope_except_file = tkinter.Button(
    master=container_scope_select, text='select a file'.upper(), command=lambda: command_select_file(text_scope_except))
button_scope_except_folder = tkinter.Button(
    master=container_scope_select, text='select a folder'.upper(),
    command=lambda: command_select_folder(text_scope_except))

container_find = tkinter.Frame(master=container_current)
label_find = tkinter.Label(master=container_find, text='find text:')
text_find = tkinter.Text(master=container_find)

container_replace = tkinter.Frame(master=container_current)
button_replace_copy = tkinter.Button(master=container_replace, text='copy text'.upper(), command=command_copy_find)
label_replace = tkinter.Label(master=container_replace, text='replace with text:')
text_replace = tkinter.Text(master=container_replace)

containers = [
    container_current,
    container_settings,
    container_modules,
    container_module_buttons,
    container_definition,
    container_browser,
    container_file_content,
    container_scope_select,
    # container_select_file,
    # container_folder_select,
    container_find,
    container_replace,
    container_command,
    container_command_buttons,
]
small_buttons = [
    button_menu_back,
]
for button_settings in list_buttons_settings:
    if list_buttons_settings.index(button_settings) < 2:
        continue
    small_buttons.append(button_settings)
large_buttons = [
    button_menu_settings,
    button_module_attach,
    button_module_retrieve,
    button_module_reload,
    button_module_browse,
    button_module_new,
    button_definition_edit,
    button_replace_copy,
    button_menu_modules,
    button_scope_select_file,
    button_scope_select_folder,
    button_scope_except_file,
    button_scope_except_folder,
    button_function_find,
    button_function_replace,
    button_run,
    button_execute,
]
labels = [
    label_modules_idle,
    label_modules_active,
    label_browser,
    label_scope_select,
    label_find,
    label_replace,
    label_scope_except
]
for setting_label in list_labels_settings:
    labels.append(setting_label)
for parameter_label in list_labels_module_editor:
    labels.append(parameter_label)
texts = [
    text_result,
    text_find,
    text_replace,
    text_file_content,
    text_scope_select,
    text_scope_except
]
for parameter_text in list_text_definition_editor:
    texts.append(parameter_text)
entries = [
]
for setting_entry in list_entry_settings:
    entries.append(setting_entry)

for button in small_buttons:
    button.place_configure(width=UNIT_WIDTH, height=UNIT_HEIGHT)
for button in large_buttons:
    button.place_configure(width=UNIT_WIDTH * 2, height=UNIT_HEIGHT)
for label in labels:
    label.place_configure(width=UNIT_WIDTH * 2, height=UNIT_HEIGHT)
for text in texts:
    text.place_configure(width=TEXT_WIDTH)
for entry in entries:
    entry.place_configure(width=TEXT_WIDTH)

try:
    image_button_small_idle = tkinter.PhotoImage(file='./aesthetic/button_small_idle.png')
    # image_button_small_hover = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_small_hover.png')
    # image_button_small_pressed = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_small_pressed.png')
    image_button_large_idle = tkinter.PhotoImage(file='aesthetic/button_large_idle.png')
    # image_button_large_hover = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_large_hover.png')
    # image_button_large_pressed = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_large_pressed.png')
    for button in small_buttons:
        button.configure(
            image=image_button_small_idle, compound='center', foreground=TEXT_COLORS[0], font=FONT_BUTTON,
            border=0, background=APP_BACKGROUND_COLOR, activebackground=APP_BACKGROUND_COLOR)
    for button in large_buttons:
        button.configure(
            image=image_button_large_idle, compound='center', foreground=TEXT_COLORS[0], font=FONT_BUTTON,
            border=0, background=APP_BACKGROUND_COLOR, activebackground=APP_BACKGROUND_COLOR)
except _tkinter.TclError:
    for button in small_buttons:
        button.configure(
            foreground=TEXT_COLORS[0], font=FONT_BUTTON,
            border=1, background=APP_BACKGROUND_COLOR, activebackground=APP_BACKGROUND_COLOR)
    for button in large_buttons:
        button.configure(
            foreground=TEXT_COLORS[0], font=FONT_BUTTON,
            border=1, background=APP_BACKGROUND_COLOR, activebackground=APP_BACKGROUND_COLOR)

for container in containers:
    container.configure(background=APP_BACKGROUND_COLOR)
for label in labels:
    label.configure(background=APP_BACKGROUND_COLOR, foreground=TEXT_COLORS[0], font=FONT_TEXT)
for text in texts:
    text.configure(
        foreground=TEXT_COLORS[0], font=FONT_TEXT, selectforeground=TEXT_COLORS[-1],
        background=ENTRY_BACKGROUND_COLOR, selectbackground=TEXT_COLORS[0])
for entry in entries:
    entry.configure(
        background=ENTRY_BACKGROUND_COLOR, foreground=TEXT_COLORS[0], font=FONT_TEXT,
        selectbackground=TEXT_COLORS[0], selectforeground=TEXT_COLORS[-1],
        disabledbackground=ENTRY_BACKGROUND_COLOR, disabledforeground=TEXT_COLORS[0])
text_result.configure(foreground=TEXT_COLORS[1])
listbox_browser.configure(
    background=ENTRY_BACKGROUND_COLOR, foreground=TEXT_COLORS[0], font=FONT_TEXT,
    selectbackground=TEXT_COLORS[0], selectforeground=TEXT_COLORS[-1])
current_style = tkinter.ttk.Style(master=main_window)
current_style.theme_use('clam')
tkinter.ttk.Style().configure(
    '.', width=UNIT_WIDTH * 2, font=FONT_TEXT, foreground=TEXT_COLORS[0], background=ENTRY_BACKGROUND_COLOR)
tkinter.ttk.Style().configure(
    'Treeview', background=ENTRY_BACKGROUND_COLOR, fieldbackground=ENTRY_BACKGROUND_COLOR, fieldbw=0,
    selectbackground=TEXT_COLORS[0], selectforeground=TEXT_COLORS[-1])
tkinter.ttk.Style().configure(
    'Treeview.Heading', borderwidth=0, overbackground=TEXT_COLORS[0], overforeground=TEXT_COLORS[-1])

for index in range(len(settings) - 1):
    list_labels_settings[index].place(x=0, y=UNIT_HEIGHT * index, width=UNIT_WIDTH * 2, height=UNIT_HEIGHT)
    list_entry_settings[index].place(x=UNIT_WIDTH * 2 + 10, y=UNIT_HEIGHT * index, width=TEXT_WIDTH - UNIT_WIDTH,
                                     height=UNIT_HEIGHT)
    if index < 2:
        list_entry_settings[index].configure(state='disabled')
        continue
    list_buttons_settings[index].place(x=TEXT_WIDTH + UNIT_WIDTH + 10, y=UNIT_HEIGHT * index,
                                       width=UNIT_WIDTH, height=UNIT_HEIGHT)

for index in range(len(DEFINITION_EXAMPLE) - 2):
    list_labels_module_editor[index].place(x=0, y=UNIT_HEIGHT * index, width=UNIT_WIDTH * 2, height=UNIT_HEIGHT)
    list_text_definition_editor[index].place(
        x=UNIT_WIDTH * 2 + 10, y=UNIT_HEIGHT * index, width=TEXT_WIDTH, height=UNIT_HEIGHT)
list_text_definition_editor[-1].place_configure(height=UNIT_HEIGHT * 4)


dict_position = {
    container_current: coordinate(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT * 13),

    label_modules_idle: coordinate(x=0, y=int(UNIT_HEIGHT * 2.5), width=UNIT_WIDTH * 2, height=UNIT_HEIGHT),
    treeview_modules_idle: coordinate(x=UNIT_WIDTH * 2, y=0, width=TEXT_WIDTH, height=UNIT_HEIGHT * 5),
    container_module_buttons: coordinate(x=UNIT_WIDTH * 0, y=UNIT_HEIGHT * 5 + 5, width=FULL_WIDTH,
                                         height=UNIT_HEIGHT + 10),
    button_module_new: coordinate(x=UNIT_WIDTH * 0, y=0),
    button_module_attach: coordinate(x=UNIT_WIDTH * 2, y=0, width=UNIT_WIDTH * 2, height=UNIT_HEIGHT),
    label_modules_active: coordinate(x=0, y=int(UNIT_HEIGHT * 9), width=UNIT_WIDTH * 2, height=UNIT_HEIGHT),
    treeview_modules_active: coordinate(x=UNIT_WIDTH * 2, y=int(UNIT_HEIGHT * 6.5), width=TEXT_WIDTH,
                                        height=UNIT_HEIGHT * 5),

    label_browser: coordinate(x=0, y=0, width=TEXT_WIDTH, height=UNIT_HEIGHT),
    listbox_browser: coordinate(x=UNIT_WIDTH * 1, y=UNIT_HEIGHT, width=TEXT_WIDTH, height=UNIT_HEIGHT * 10),

    label_scope_select: coordinate(x=0, y=0),
    text_scope_select: coordinate(x=UNIT_WIDTH*2, y=UNIT_HEIGHT*0, width=TEXT_WIDTH-UNIT_WIDTH*4, height=UNIT_HEIGHT),
    button_scope_select_file: coordinate(x=TEXT_WIDTH - UNIT_WIDTH * 2, y=UNIT_HEIGHT * 0),
    button_scope_select_folder: coordinate(x=TEXT_WIDTH, y=UNIT_HEIGHT * 0),
    label_scope_except: coordinate(x=0, y=UNIT_HEIGHT * 1),
    text_scope_except: coordinate(x=UNIT_WIDTH*2, y=UNIT_HEIGHT*1, width=TEXT_WIDTH-UNIT_WIDTH*4, height=UNIT_HEIGHT),
    button_scope_except_file: coordinate(x=TEXT_WIDTH - UNIT_WIDTH*2, y=UNIT_HEIGHT*1),
    button_scope_except_folder: coordinate(x=TEXT_WIDTH, y=UNIT_HEIGHT*1),

    text_file_content: coordinate(x=UNIT_WIDTH * 1, y=0, width=TEXT_WIDTH, height=UNIT_HEIGHT * 12),
    numeration: coordinate(x=0, y=0, width=UNIT_WIDTH - 1, height=UNIT_HEIGHT * 12),
    label_find: coordinate(x=0, y=0, width=UNIT_WIDTH * 2, height=UNIT_HEIGHT),
    text_find: coordinate(x=UNIT_WIDTH * 2, y=0, width=TEXT_WIDTH, height=UNIT_HEIGHT),
    button_replace_copy: coordinate(x=0, y=0),
    label_replace: coordinate(x=0, y=UNIT_HEIGHT),
    text_replace: coordinate(x=UNIT_WIDTH * 2, y=0, width=TEXT_WIDTH, height=UNIT_HEIGHT * 2),
    # container_command:
    text_result: coordinate(x=0, y=0, width=FULL_WIDTH, height=int(UNIT_HEIGHT * 0.75)),
    container_command_buttons: coordinate(x=0, y=UNIT_HEIGHT * 2, anchor='sw', width=FULL_WIDTH, height=UNIT_HEIGHT),
    button_menu_back: coordinate(x=0, y=0),
    button_menu_modules: coordinate(x=UNIT_WIDTH * 1, y=0),
    button_menu_settings: coordinate(x=UNIT_WIDTH * 3, y=0),
    button_run: coordinate(x=UNIT_WIDTH * 5, y=0),
    button_execute: coordinate(x=UNIT_WIDTH * 7, y=0),
    # button_function_duplicate: coordinate(x=UNIT_WIDTH * 9, y=0),
    button_function_find: coordinate(x=UNIT_WIDTH * 11, y=0),
    button_function_replace: coordinate(x=UNIT_WIDTH * 13, y=0),

    # non-default
    container_modules: coordinate(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT * 13),
    button_module_browse: coordinate(x=UNIT_WIDTH * 8, y=0, width=UNIT_WIDTH * 2, height=UNIT_HEIGHT),
    button_definition_edit: coordinate(x=UNIT_WIDTH * 12, y=0, width=UNIT_WIDTH * 2, height=UNIT_HEIGHT),
    button_module_retrieve: coordinate(x=UNIT_WIDTH * 4, y=0, width=UNIT_WIDTH * 2, height=UNIT_HEIGHT),
    button_module_reload: coordinate(x=UNIT_WIDTH * 6, y=0, width=UNIT_WIDTH * 2, height=UNIT_HEIGHT),

    container_command: coordinate(x=0, y=UNIT_HEIGHT * 15, anchor='sw', width=FULL_WIDTH, height=UNIT_HEIGHT * 2),
    container_settings: coordinate(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT * 11),
    container_definition: coordinate(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT * 11),
    container_browser: coordinate(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT * 12),
    # container_select_file: coordinate(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT * 2),
    # container_folder_select: coordinate(x=0, y=UNIT_HEIGHT * 2, width=FULL_WIDTH, height=UNIT_HEIGHT * 3),
    container_scope_select: coordinate(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT * 2),
    container_file_content: coordinate(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT * 13),
    container_find: coordinate(x=0, y=int(UNIT_HEIGHT * 7.5), width=FULL_WIDTH, height=UNIT_HEIGHT * 1),
    container_replace: coordinate(x=0, y=int(UNIT_HEIGHT * 8.5), width=FULL_WIDTH, height=UNIT_HEIGHT * 2),
}

position(
    container_current, text_result,
    container_command_buttons, button_menu_back, button_menu_modules, button_menu_settings, button_run,
    button_execute, button_function_find, button_function_replace,
    container_module_buttons, button_module_new, button_module_attach,
    text_file_content, numeration, label_browser, listbox_browser,
    label_modules_idle, treeview_modules_idle, label_modules_active, treeview_modules_active,
    label_scope_select, button_scope_select_file, button_scope_select_folder, text_scope_select,
    label_scope_except, button_scope_except_file, button_scope_except_folder, text_scope_except,
    label_find, text_find, button_replace_copy, label_replace, text_replace,
)  #

set_window_modules()
main_window.protocol("WM_DELETE_WINDOW", on_app_close)
main_window.mainloop()

_all_defined = [
    # local constants
    UNIT_WIDTH,
    UNIT_HEIGHT,
    TEXT_WIDTH,
    FULL_WIDTH,
    LIST_WIDTH,
    MODULE_COLUMNS,
    # global variables
    global_modules,
    current_path,
    current_levels,
    current_file_content_backup,
    current_window,
    new_module_name,
    new_module_source,
    # constant initiating functions
    load_font,
    load_colors,
    # closing handlers
    warning_file_save,
    on_app_close,
    # display functions
    clear_window,
    # set_window_controller,
    set_window_settings,
    set_window_modules,
    set_window_definition,
    set_window_browser,
    set_window_file,
    set_window_move,
    set_window_find,
    set_window_replace,
    # snapshot functions
    command_snapshot_take,
    command_snapshot_compare,
    # settings functions
    command_settings_save,
    command_settings_reload,
    # module functions
    on_select_module_idle,
    on_select_module_active,
    command_module_new,
    command_module_copy,
    command_module_attach,
    command_module_retrieve,
    command_module_reload,
    command_module_browse,
    # definition functions
    refresh_definitions,
    command_definition_save,
    # browser functions
    command_browser_forward,
    command_browser_back,
    open_browser_item,
    # text editor functions
    command_file_load,
    command_file_save,
    command_text_comment,
    command_text_uncomment,
    set_text_color,
    # file editor functions
    command_run_move,
    command_run_duplicate,
    command_run_find,
    command_run_replace,

    dict_position,
    coordinate,
    position,
    retrieve,
]
