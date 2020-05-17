#!/usr/bin/env python3
# Скрипт для создания файловой структуры "Nested", методология БЭМ.
# В рамках данного скрипта я использую термин "БЭМ-компонент", имея ввиду любую
# БЭМ-сущность, т.е. и БЭМ-блок и БЭМ-элемент и БЭМ-модификатор.

# Импорт библиотеки "BeautifulSoup4" для извлечения данных из HTML-файла и
# модулей, являющихся частью стандартной библиотеки Python 3.
from bs4 import BeautifulSoup
import json
import os
import re

# Требуем от пользователя ввести путь к HTML-файлу.
HTML_FILE: str = input('Введите путь к HTML-файлу: ')

# Проверяем наличие HTML-файла. В случае его отсутствия печатаем на экране
# служебное сообщение и завершаем работу скрипта.
if not os.path.exists(HTML_FILE):
    print('HTML-файл {} не найден.'.format(HTML_FILE))
else:
    with open(HTML_FILE, encoding='utf-8') as fp:
        soup = BeautifulSoup(fp, 'html.parser')


    def get_list_of_tags() -> list:
        """ Функция возвращает список объектов, являющихся HTML-элементами,
            содержащимися в HTML-файле """
        return soup.find_all(True)


    def get_list_of_tags_having_classes() -> list:
        """ Функция возвращает список объектов, являющихся HTML-элементами,
            имеющими атрибут class """
        return list(filter(lambda tag: tag.has_attr('class'), get_list_of_tags()))


    def get_set_of_classes() -> set:
        """ Функция возвращает множество строк, содержащих имена классов
            HTML-элементов """
        list_of_classes = []
        for tag in get_list_of_tags_having_classes():
            list_of_classes.extend(tag.get('class'))
        return set(list_of_classes)


    def get_json_file_path() -> str:
        """ Функция возвращает строку, содержащую путь к JSON-файлу """
        return '../.listOfUsedClasses.json'
    

    def write_json_file(list_of_classes: list = []) -> None:
        """ Функция, получив путь к JSON-файлу с помощью функции get_json_file_path,
            преобразовывает исходный тип данных в JSON-строку и записывает ее в
            данный файл """
        with open(get_json_file_path(), 'wt') as json_file:
            json_file.write(json.dumps({'used_classes': list_of_classes}, indent='\t'))


    def read_json_file() -> dict:
        """ Функция, получив путь к JSON-файлу с помощью функции get_json_file_path,
            прочитывает такой файл и преобразовывает JSON-строку в исходный тип
            данных, возвращаяя словарь """
        with open(get_json_file_path()) as json_file:
            return json.loads(json_file.read())


    def get_set_of_used_classes() -> set:
        """ Функция возвращает множество строк, содержащих имена классов HTML-элементов,
            имеющих файловую структуру """
        return set(read_json_file()['used_classes'])
        
        
    def get_set_of_new_classes() -> set:
        """ Функция возвращает множество строк, содержащих имена классов HTML-элементов,
            не имеющих файловой структуры """
        return get_set_of_classes() - get_set_of_used_classes()
                

    def get_name_pattern() -> str:
        """ Функция возвращает строку, содержащую шаблон, который используется
            для создания шаблонов имен БЭМ-компонентов """
        return '[a-z]+(-[a-z]+)?'


    def get_bem_component_name_pattern(component_name: str) -> str:
        """ Функция, руководствуясь значением параметра component_name, возвращает
            строку, содержащую либо шаблон имени БЭМ-компонента либо сообщение об
            ошибке """
        NAME_PATTERN = get_name_pattern()
        dict_of_patterns = {
            'block': '{}'.format(NAME_PATTERN),
            'block modifier': '{0}(_{0}){1}'.format(NAME_PATTERN, '{1,2}'),
            'element': '{0}__{0}'.format(NAME_PATTERN),
            'element modifier': '{0}__{0}(_{0}){1}'.format(NAME_PATTERN, '{1,2}')
        }
        ERROR_MSG = '[ValueError]: component_name is undefined'
        return dict_of_patterns.get(component_name, ERROR_MSG)


    def is_bem_component(component_name: str, class_name: str) -> bool:
        """ Функция определяет соответствует ли HTML-элемент с классом class_name
            БЭМ-компоненту, определенному параметром component_name, возвращая
            одно из двух булевых значений """
        COMPONENT_NAME_PATTERN = \
            re.compile('^{}$'.format(get_bem_component_name_pattern(component_name)))
        return bool(COMPONENT_NAME_PATTERN.match(class_name))


    def get_list_of_bem_components(component_name: str, classes) -> list:
        """ Функция производит фильтрацию списка (множества) classes и возвращает
            список строк, содержащих имена классов HTML-элементов, соответствующих
            БЭМ-компоненту, определенному параметром component_name """
        return list(filter(
            lambda class_name: is_bem_component(component_name, class_name), classes
        ))


    def get_bem_component_path_pattern(component_name: str) -> str:
        """ Функция, руководствуясь значением параметра component_name, возвращает
            строку, содержащую либо шаблон пути к БЭМ-компоненту либо сообщение
            об ошибке """
        dict_of_patterns = {
            'block': './{}',
            'block modifier': './{}/{}',
            'element': './{}/{}',
            'element modifier': './{}/{}/{}'
        }
        ERROR_MSG = '[ValueError]: component_name is undefined'
        return dict_of_patterns.get(component_name, ERROR_MSG)


    def create_css_file(class_name: str) -> None:
        """ Функция, руководствуясь значением параметра class_name, создает CSS-файл,
            записывая в него селектор класса """
        with open('{}.css'.format(class_name), 'wt') as css_file:
            css_file.write('.{} {}'.format(class_name, '{\n\n}'))


    def create_dirs_and_files_for_bem_components(component_name: str) -> None:
        """ Функция, руководствуясь значением параметра component_name, создает
            каталоги и CSS-файлы для БЭМ-компонентов, не имеющих файловой структуры """
        new_components = \
            get_list_of_bem_components(component_name, get_set_of_new_classes())
        PATH_PATTERN = get_bem_component_path_pattern(component_name)
        NAME_PATTERN = get_name_pattern()

        for component in new_components:
            if component_name == 'block':
                DIR_PATH = PATH_PATTERN.format(component)
            elif component_name == 'block modifier':
                DIR_PATH = PATH_PATTERN.format(
                    re.match(NAME_PATTERN, component).group(),
                    re.search('_{}'.format(NAME_PATTERN), component).group()
                )
            elif component_name == 'element':
                DIR_PATH = PATH_PATTERN.format(
                    re.match(NAME_PATTERN, component).group(),
                    re.search('__{}'.format(NAME_PATTERN), component).group()
                )
            elif component_name == 'element modifier':
                DIR_PATH = PATH_PATTERN.format(
                    re.match(NAME_PATTERN, component).group(),
                    re.search('__{}'.format(NAME_PATTERN), component).group(),
                    [result.group() for result in re.finditer('_{}'.format(NAME_PATTERN), component)][1]
                )

            if not os.path.exists(DIR_PATH):
                os.mkdir(DIR_PATH)
                
            FILE_PATH = '{}/{}.css'.format(DIR_PATH, component)
            if not os.path.exists(FILE_PATH):
                BLOCKS_DIR = os.path.abspath('./')
                os.chdir(DIR_PATH)
                create_css_file(component)
                os.chdir(BLOCKS_DIR)
        
                   
    def create_fs_nested() -> None:
        """ Функция, используя функцию create_dirs_and_files_for_bem_components,
            создает файловую структуру Nested, соответствующую HTML-файлу """
        create_dirs_and_files_for_bem_components('block')
        create_dirs_and_files_for_bem_components('block modifier')
        create_dirs_and_files_for_bem_components('element')
        create_dirs_and_files_for_bem_components('element modifier')


    def get_main_css_file_path() -> str:
        """ Функция возвращает строку, содержащую путь к основному CSS-файлу """
        return './{}'.format(HTML_FILE.replace('html', 'css'))


    def write_main_css_file(import_string: str = '') -> None:
        """ Функция, получив путь к основному CSS-файлу с помощью функции
            get_main_css_file_path, записывает значение import_string, переданное
            ей в качестве аргумента, в данный файл """
        with open(get_main_css_file_path(), 'at') as css_file:
            css_file.write(import_string)


    def read_main_css_file() -> str:
        """ Функция, получив путь к основному CSS-файлу с помощью функции
            get_main_css_file_path, прочитывает такой файл, возвращая строку """
        with open(get_main_css_file_path()) as css_file:
            return css_file.read()


    def include_in_current_import_string(import_string: str) -> bool:
        """ Функция определяет, входит ли директива подключения БЭМ-блока,
            определенная параметром import_string, в основной CSS-файл, возвращая
            одно из двух булевых значений """
        IMPORT_STRING_PATTERN = re.compile('^{}$'.format(read_main_css_file()))
        return bool(IMPORT_STRING_PATTERN.search(import_string))


    def get_import_string() -> str:
        """ Функция в случае необходимости возвращает строку, содержащую директивы
            подключения БЭМ-блоков к основному CSS-файлу (@import url()), а в случае
            ее отсутствия - пустую строку """
        NEW_BLOCKS: list = \
            get_list_of_bem_components('block', get_set_of_new_classes())
        new_import_string: str = ''

        for BLOCK in NEW_BLOCKS:
            BLOCK_IMPORT_STRING = '@import url(../blocks/{0}/{0}.css);'.format(BLOCK)
            if not include_in_current_import_string(BLOCK_IMPORT_STRING):
                new_import_string += (BLOCK_IMPORT_STRING + '\n')

        return new_import_string


    # Проверяем наличие каталога blocks. В случае его отсутствия, создаем в каталоге,
    # содержащем данный сценарий, и переходим в него.
    if not os.path.exists('./blocks'):
        os.mkdir('./blocks')
    os.chdir('./blocks')

    # Проверяем наличие JSON-файла. В случае его отсутствия, создаем в текущем
    # каталоге, т.е. каталоге blocks.
    if not os.path.exists(get_json_file_path()):
        write_json_file()

    # Создаем файловую структуру. Подробности в документациях функций.
    create_fs_nested()

    # Возвращаемся из каталога blocks в корневой каталог.
    os.chdir('../')

    # Проверяем наличие каталога pages. В случае его отсутствия, создаем в каталоге,
    # содержащем данный сценарий, и переходим в него.
    if not os.path.exists('./pages'):
        os.mkdir('./pages')
    os.chdir('./pages')
    
    # Проверяем наличие основного CSS-файла. В случае его отсутствия, создаем в
    # текущем каталоге, т.е. каталоге pages, и записываем в него определенную
    # строковую константу.
    if not os.path.exists(get_main_css_file_path()):
        write_main_css_file('/* @import url(../vendor/normalize.css); */\n')
        
    # Записываем в основной CSS-файл строку, полученную в результате вызова
    # функции get_import_string
    write_main_css_file(get_import_string())

    # Записываем множество классов HTML-элементов в JSON-файл, отсортировав их
    # в алфавитном порядке.
    write_json_file(sorted(list(get_set_of_classes())))

    # Возвращаемся из каталога pages в корневой каталог.
    os.chdir('../')

print('Сценарий завершил работу.')
