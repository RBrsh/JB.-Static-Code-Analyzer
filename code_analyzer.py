class CodeAnalyzer:
    def __init__(self, path_to_file):
        self.path_to_file = path_to_file
        self.__error_messages = {
            'S001': 'Line is too long',
            'S002': 'Indentation is not a multiple of four',
            'S003': 'Unnecessary semicolon after a statement',
            'S004': 'Less than two spaces before inline comments',
            'S005': 'TODO found',
            'S006': 'More than two blank lines preceding a code line '
        }
        self.__error_codes = {
            '__check_line_length': 'S001',
            '__check_indentation': 'S002',
            '__check_semicolon': 'S003',
            '__check_spaces': 'S004',
            '__check_todo': 'S005',
            '__check_blank_lines': 'S006'
        }
        self.__errors = []

        self.__line_length_limit = 79

        self.__checks = []
        self.__check_method_prefix = '__check_'
        self.__prepare_checks()

    def perform_checks(self):
        with open(self.path_to_file) as fh:
            for ln, l in enumerate(fh.readlines(), 1):
                for m in self.__checks:
                    check_result = m(l, m.__name__)

                    if check_result:
                        self.__errors.append(check_result)

    def __check_line_length(self, line: str, method_name: str) -> str:
        """
        Checks passed line of code to be less or equal to the line length
        limit, which is 79.

        :param line: Code line to be processed.
        :param method_name: Used as a key for error codes dictionary.
        :return: Error code as a string or an empty string in case there was no
        error.
        """

        res = ''

        if len(line) > self.__line_length_limit:
            res = self.__error_codes[method_name]
        return res

    def __check_indentation(self, line: str, method_name: str) -> str:
        """
        Checks passed line of code to be indented with amount of spaces
        multiple of 4.

        :param line: Code line to be processed.
        :param method_name: Used as a key for error codes dictionary.
        :return: Error code as a string or an empty string in case there was no
        error.
        """
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

    def __check_semicolon(self, line: str, method_name: str):
        #print(self.__is_in_string(line, 14))
        pass

    def __check_spaces(self, line: str, method_name: str):
        pass

    def __check_todo(self, line: str, method_name: str):
        pass

    def __check_blank_lines(self, line: str, method_name: str):
        pass

    def __is_in_comment(self, line: str, pos: int) -> bool:
        """
        Checks if passed ... in a comment.

        :param line: Line of code to be processed
        :param pos: Position of found error in passed line
        :return: True if the passed position is in a string, False otherwise.
        """
        slcs = '#'  # Single line comment symbol
        start = 0

        while True:
            fp = line.find(slcs, start, pos - 1 if pos > 0 else None)
            if fp > -1:
                if self.__is_in_string(line, fp):
                    start = fp
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
                fp = line.find(s, start, pos - 1 if pos > 0 else None)
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

    def __prepare_checks(self):
        for mn in self.__dir__():
            if mn.startswith(f'_{type(self).__name__}'
                             f'{self.__check_method_prefix}'):
                m = getattr(self, mn)
                if callable(m):
                    self.__checks.append(m)

    def get_errors(self):
        return self.__errors


def main():
    code_analyzed = CodeAnalyzer('tmp_test.py')
    code_analyzed.perform_checks()
    print(code_analyzed.get_errors())


if __name__ == '__main__':
    main()
