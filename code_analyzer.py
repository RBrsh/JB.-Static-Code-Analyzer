import sys
import os
import re


class CodeAnalyzer:
    def __init__(self, path_to_file):
        self.path_to_file = path_to_file
        self.__code_lines = []

        self.__error_messages = {
            'S001': 'Line exceed characters limit',
            'S002': 'Indentation is not a multiple of four',
            'S003': 'Unnecessary semicolon after a statement',
            'S004': 'Less than two spaces before inline comments',
            'S005': 'TODO found',
            'S006': 'More than two blank lines preceding a code line',
            'S007': 'Too many spaces after construction_name',
            'S008': 'Class name class_name should be written in CamelCase',
            'S009': 'Function name function_name should be written in '
                    'snake_case'
        }
        self.__error_codes = {
            '__check_line_length': 'S001',
            '__check_indentation': 'S002',
            '__check_semicolon': 'S003',
            '__check_spaces_before_comment': 'S004',
            '__check_todo': 'S005',
            '__check_blank_lines': 'S006',
            '__check_spaces_after_name': 'S007',
            '__check_class_name': 'S008',
            '__check_function_name': 'S009'
        }
        self.__errors = {}

        self.__line_length_limit = 79
        self.__min_spaces_before_comment = ' ' * 2
        self.__todo_flag = 'todo'
        self.__comment_flag = '#'
        self.__construction_names = {
            'class_keyword': 'class',
            'function_keyword': 'def'
        }
        self.__max_blank_lines_before = 2

        self.__check_method_prefix = '__check_'
        self.__checks = []
        self.__prepare_checks()

    def perform_checks(self) -> None:
        with open(self.path_to_file) as fh:
            self.__code_lines = fh.readlines()

            for ln in range(1, len(self.__code_lines) + 1):
                lcr = []  # Line check results
                for m in self.__checks:
                    check_result = m(ln, m.__name__)

                    if check_result:
                        lcr.append(check_result)

                if lcr:
                    lcr.sort()
                    self.__errors.update({ln: lcr})

    def __check_line_length(self, line_number: int, method_name: str) -> str:
        """
        Checks line of code to be within the line length limit.

        :param line_number: Code line number to be processed.
        :param method_name: Used as a key for error codes dictionary.
        :return: Error code as a string or an empty string in case there was no
        error.
        """
        line = self.__code_lines[line_number - 1]
        res = ''

        if len(line) > self.__line_length_limit:
            res = self.__error_codes[method_name]
        return res

    def __check_indentation(self, line_number: int, method_name: str) -> str:
        """
        Checks line of code to be indented with amount of spaces multiple of 4.

        :param line_number: Code line number to be processed.
        :param method_name: Used as a key for error codes dictionary.
        :return: Error code as a string or an empty string in case there was no
        error.
        """
        line = self.__code_lines[line_number - 1]
        res = ''
        spaces_counter = 0

        if line and line[0] == ' ':
            for c in line:
                if c == ' ':
                    spaces_counter += 1
                else:
                    break

            if (spaces_counter % 4) != 0:
                res = self.__error_codes[method_name]

        return res

    def __check_semicolon(self, line_number: int, method_name: str) -> str:
        """
        Checks if there is an unnecessary semicolon in the passed code line.
        Meaning it is not in a comment or a string.

        :param line_number: Code line number to be processed.
        :param method_name: Used as a key for error codes dictionary.
        :return: Error code as a string or an empty string in case there was no
        error.
        """
        line = self.__code_lines[line_number - 1]
        res = ''

        for i in range(len(line)):
            if line[i] == ';':
                if self.__is_in_string(line, i) or \
                        self.__is_in_comment(line, i):
                    continue

                res = self.__error_codes[method_name]
                break

        return res

    def __check_spaces_before_comment(self, line_number: int,
                                      method_name: str) -> str:
        """
        Checks if there are at least two spaces before an inline comment.

        :param line_number: Code line number to be processed.
        :param method_name: Used as a key for error codes dictionary.
        :return: Error code as a string or an empty string in case there was no
        error.
        """
        line = self.__code_lines[line_number - 1]
        res = ''
        start = 0

        while True:
            lsl = line.lstrip()
            if lsl and lsl[0] == self.__comment_flag:
                break

            fp = line.find(self.__comment_flag, start)

            if fp > - 1:
                if self.__is_in_string(line, fp):
                    start = fp + 1
                    continue

                if line[fp - 2:fp] != self.__min_spaces_before_comment:
                    res = self.__error_codes[method_name]

            break

        return res

    def __check_todo(self, line_number: int, method_name: str) -> str:
        """
        Checks if there is a to-do in a comment.

        :param line_number: Code line number to be processed.
        :param method_name: Used as a key for error codes dictionary.
        :return: Error code as a string or an empty string in case there was no
        error.
        """
        line = self.__code_lines[line_number - 1]
        res = ''
        start = 0

        while True:
            fp = line.lower().find(self.__todo_flag, start)

            if fp > -1:
                if self.__is_in_comment(line, fp):
                    res = self.__error_codes[method_name]
                    break

                start = fp + 1
                continue

            break

        return res

    def __check_blank_lines(self, line_number: int, method_name: str) -> str:
        """
        Checks if there are at least two blank lines before line.

        :param line_number: Code line number to be processed.
        :param method_name: Used as a key for error codes dictionary.
        :return: Error code as a string or an empty string in case there was no
        error.
        """
        line = self.__code_lines[line_number - 1]
        res = ''

        if line_number > self.__max_blank_lines_before and line.strip():
            counter = 0
            for i in range(2, self.__max_blank_lines_before + 3):
                if not self.__code_lines[line_number - i].strip():
                    counter += 1

            if counter > self.__max_blank_lines_before:
                res = self.__error_codes[method_name]

        return res

    def __check_spaces_after_name(self, line_number: int, method_name: str)\
            -> str:
        line = self.__code_lines[line_number - 1]
        res = ''

        for k, v in self.__construction_names.items():
            fp = line.find(v)

            if fp > -1:
                if self.__is_in_comment(line, fp) and \
                        self.__is_in_string(line, fp):
                    continue

                offset = fp + len(v)
                if line[offset:offset + 2] == '  ':
                    res = f'{self.__error_codes[method_name]}' \
                          f' {self.__error_messages[self.__error_codes[method_name]]}'.replace('construction_name',
                                                                                                f"'{v}'")

                break

        return res

    def __check_class_name(self, line_number: int, method_name: str) -> str:
        line = self.__code_lines[line_number - 1]
        flag = self.__construction_names['class_keyword']
        stub = 'class_name'
        res = ''

        fp = line.lower().find(flag)

        if fp > -1:
            if not self.__is_in_comment(line, fp) and \
                    not self.__is_in_string(line, fp):
                good_pattern = r'^ +([A-Z][a-z]+([A-Z][a-z]+)*) *[:(]*'

                if not re.match(good_pattern, line[fp + len(flag):]):
                    bad_pattern = r'^ +(\w+) *[:(]*'
                    m = re.match(bad_pattern, line[fp + len(flag):])
                    assert m, line

                    class_name = f"'{m.group(1)}'"
                    msg = self.__error_messages[self.__error_codes[method_name]]
                    res = f'{self.__error_codes[method_name]} ' \
                      f'{msg.replace(stub, class_name)}'

        return res

    def __check_function_name(self, line_number: int, method_name: str) -> str:
        line = self.__code_lines[line_number - 1]
        flag = self.__construction_names['function_keyword']
        stub = 'function_name'
        res = ''

        fp = line.lower().find(flag)

        if fp > -1:
            if not self.__is_in_comment(line, fp) and \
                    not self.__is_in_string(line, fp):
                good_pattern = r'^ +[_]{,2}[a-z]+([_][a-z]+)*[__]{,2}\b\(*'

                if not re.match(good_pattern, line[fp + len(flag):]):
                    bad_pattern = r'^ +(\w+) *\('
                    m = re.match(bad_pattern, line[fp + len(flag):])
                    assert m

                    func_name = f"'{m.group(1)}'"
                    msg = self.__error_messages[self.__error_codes[method_name]]
                    res = f'{self.__error_codes[method_name]} ' \
                      f'{msg.replace(stub, func_name)}'

        return res

    def __is_in_comment(self, line: str, pos: int) -> bool:
        """
        Checks if passed position of the code line is in a comment.

        :param line: Line of code to be processed
        :param pos: Position of found error in passed line
        :return: True if the passed position is in a comment, False otherwise.
        """
        start = 0

        while True:
            fp = line.find(self.__comment_flag, start, pos if pos > 0 else None)
            if fp > -1:
                if self.__is_in_string(line, fp):
                    start = fp + 1
                else:
                    return True
            else:
                break

        return False

    def __is_in_string(self, line: str, pos: int) -> bool:
        """
        Checks if passed position is in a string: between single or double
        quotes. Not really between, just checking if there is an opening qute
        before the position.

        :param line: Line of code
        :param pos: Position being checked
        :return: True if passed position is in a string. False otherwise.
        """
        slss = ["'", '"']  # Single line string symbols
        start = 0
        result = []

        for s in slss:
            while True:
                fp = line.find(s, start, pos if pos > 0 else None)
                if fp > -1:
                    start = fp + 1
                    if line[fp - 1] == '\\':
                        continue
                    result.append(line[fp])
                else:
                    break

        if result:
            opened = None

            for i in range(len(result)):
                if opened is None:
                    opened = result[i]
                elif opened == result[i]:
                    opened = None

            if opened:
                return True
        return False

    def __prepare_checks(self) -> None:
        """
        Looks for callable methods with a prefix set in __check_method_prefix.
        Adds found method to the __checks list to be called during the code
        analyzation.

        :return: None
        """
        for mn in self.__dir__():
            if mn.startswith(f'_{type(self).__name__}'
                             f'{self.__check_method_prefix}'):
                m = getattr(self, mn)
                if callable(m):
                    self.__checks.append(m)

    def get_errors(self) -> list:
        res = []

        if self.__errors:
            for ln, le in self.__errors.items():
                for e in le:
                    if e in self.__error_messages.keys():
                        res.append(f'{self.path_to_file}: '
                                   f'Line {ln}: {e} {self.__error_messages[e]}')
                    else:
                        res.append(f'{self.path_to_file}: Line {ln}: {e}')

        return res


def prep_path_to_files(path):
    result = []

    if os.path.isfile(path):
        result.append(path)
    elif os.path.isdir(path):
        for p in os.scandir(path):
            if p.is_file():
                result.append(p.path)
            elif p.is_dir():
                result.extend(prep_path_to_files(p.path))

    result = [i for i in result if os.path.splitext(i)[1] == '.py']
    return result


def main():
    assert sys.argv[1]

    file_list = ['tmp_test.py']
    errors = []

    if os.path.exists(sys.argv[1]):
        file_list = prep_path_to_files(sys.argv[1])
        file_list.sort()

    for p in file_list:
        code_analyzed = CodeAnalyzer(p)
        code_analyzed.perform_checks()
        errors.extend(code_analyzed.get_errors())

    if errors:
        print(*errors, sep='\n')


if __name__ == '__main__':
    main()
