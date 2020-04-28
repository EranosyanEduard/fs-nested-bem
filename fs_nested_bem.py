#!/usr/bin/env python3
# Скрипт для создания файловой структуры "Nested", методология БЭМ

# Импорт библиотеки "BeautifulSoup4" для извлечения данных из HTML-файла и
# модулей, являющихся частью языка программирования Python 3
from bs4 import BeautifulSoup
import glob
import json
import os
import shutil

# Требуем от пользователя ввести путь к HTML-файлу
HTML_FILE = input('Введите путь к HTML-файлу: ')

# Проверяем наличие HTML-файла. В случае его отсутствия печатаем на экране
# служебное сообщение и завершаем работу скрипта
if not os.path.exists(HTML_FILE):
    print('HTML-файл {} не найден.'.format(HTML_FILE))
else:
    with open(HTML_FILE, encoding='utf-8') as fp:
        soup = BeautifulSoup(fp, 'html.parser')


    def get_list_of_tags():
        """ Функция возвращает список всех HTML-тэгов, имеющихся в файле HTML_FILE """
        return soup.find_all(True)


    def get_list_of_tags_having_classes():
        """ Функция, используя функцию get_list_of_tags, возвращает список HTML-тэгов,
        имеющих атрибут class """
        return list(filter(lambda tag: tag.has_attr('class'), get_list_of_tags()))


    def get_set_of_classes():
        """ Функция, используя функцию get_list_of_tags_having_classes, возвращает
        множество классов HTML-тэгов """
        list_of_classes = []
        for tag in get_list_of_tags_having_classes():
            list_of_classes.extend(tag.get('class'))
        return set(list_of_classes)


    def get_json_file_path():
        """ Функция возвращает строку - путь к JSON-файлу """
        return 'listOfUsedClasses.json'
    

    def write_json_file(list_of_classes=[]):
        """ Функция, используя функцию get_json_file_path, записывает данные в JSON-файл,
        предварительно преобразовав их в JSON-строку """
        with open(get_json_file_path(), 'wt') as json_file:
            json_file.write(json.dumps({'current_list_of_classes': list_of_classes}, indent='\t'))


    def read_json_file():
        """ Функция, используя функцию get_json_file_path, возвращает словарь,
        после прочтения JSON-файла и преобразования JSON-строки в исходный тип данных """
        with open(get_json_file_path()) as json_file:
            return json.loads(json_file.read())


    def get_set_of_used_classes():
        """ Функция, используя функцию read_json_file, возвращает множество,
        элементами которого являются классы HTML-тэгов, для которых создана
        файловая структура Nested """
        return set(read_json_file()['current_list_of_classes'])
        
        
    def get_set_of_new_classes():
        """ Функция, используя функции get_set_of_classes и get_set_of_used_classes,
        возвращает множество, элементами которого являются классы HTML-тэгов,
        для которых не создана файловая структура Nested """
        return get_set_of_classes() - get_set_of_used_classes()


    def create_dirs_and_css_files():
        """ Функция, используя функцию get_set_of_new_classes, создает каталоги и
        CSS-файлы для каждого элемента множества, т.е. класса, для которого не создана
        файловая структура Nested """
        for class_name in get_set_of_new_classes():
            os.mkdir(class_name)
            with open('{0}/{0}.css'.format(class_name), 'wt') as css_file:
                css_file.write('.{} {}'.format(class_name, '{}'))
                

    def get_list_of_blocks():
        """ Функция, используя функцию get_set_of_classes, возвращает
        список, элементами которого являются классы HTML-тегов - БЭМ-блоки """
        return list(filter(lambda class_name: '_' not in class_name, get_set_of_classes()))


    def move_elements_and_modifiers_to_blocks():
        """ Функция, используя функцию get_list_of_blocks, перемещает файлы БЭМ-элементов
        и БЭМ-модификаторов в соответствующие им каталоги БЭМ-блоков """
        for block in get_list_of_blocks():
            for element_or_modifier in glob.glob('{}_*'.format(block)):
                shutil.move(element_or_modifier, block)


    def rename_element_and_modifier_dirs():
        """ Функция, используя функцию get_list_of_blocks, переименовывает каталоги
        БЭМ-элементов и БЭМ-модификаторов, содержащие имена БЭМ-блоков, например
        из header__link в __link или из logo_place_header в _place_header """
        for block in get_list_of_blocks():
            os.chdir(block)
            for dir_name in glob.glob('{}_*'.format(block)):
                os.rename(dir_name, dir_name.replace(block, ''))
            os.chdir('..')


    def move_element_modifiers_to_elements():
        """ Функция, используя функцию get_list_of_blocks, создает каталоги БЭМ-модификаторов
        в соответствующих им каталогах БЭМ-элементов и перемещает в них CSS-файлы таких
        модификаторов, при этом удаляя лишние каталоги """
        for block in get_list_of_blocks():
            os.chdir(block)
            for dir_name in glob.glob('__*_*'):
                element = dir_name[2:].split('_')[0]
                modifier = dir_name[2:].split('_')[1]
                modifier_dir_path = '__{}/_{}'.format(element, modifier)
                if not os.path.exists(modifier_dir_path):
                    os.mkdir(modifier_dir_path)
                os.chdir(dir_name)
                shutil.move(os.listdir()[0], '../{}'.format(modifier_dir_path))
                os.chdir('..')
                os.rmdir(dir_name)
            os.chdir('..')


    def move_block_modifiers_to_modifiers():
        """ Функция, используя функцию get_list_of_blocks, создает каталоги БЭМ-модификаторов
        в соответствующих им каталогах БЭМ-блоков и перемещает в них CSS-файлы таких
        модификаторов, при этом удаляя лишние каталоги """
        for block in get_list_of_blocks():
            os.chdir(block)
            for dir_name in glob.glob('_[a-z]*_*'):
                modifier = dir_name[1:].split('_')[0]
                modifier_dir_path = '_{}'.format(modifier)
                if not os.path.exists(modifier_dir_path):
                    os.mkdir(modifier_dir_path)
                os.chdir(dir_name)
                shutil.move(os.listdir()[0], '../{}'.format(modifier_dir_path))
                os.chdir('..')
                os.rmdir(dir_name)
            os.chdir('..')
        
                   
    # Создание каталога blocks в случае его отсутствия в каталоге, содержащем данный сценарий
    if not os.path.exists('blocks'):
        os.mkdir('blocks')
    # Переход в каталог blocks
    os.chdir('blocks')

    # Создание JSON-файла в случае его отсутствия в каталоге, содержащем данный сценарий
    if not os.path.exists(get_json_file_path()):
        write_json_file()

    # См. документации соответствующих функций
    create_dirs_and_css_files()
    move_elements_and_modifiers_to_blocks()
    rename_element_and_modifier_dirs()
    move_element_modifiers_to_elements()
    move_block_modifiers_to_modifiers()    
    write_json_file(list(get_set_of_classes()))

print('Сценарий завершил работу.')
