class CodeAnalyzer:
    def __init__(self, path_to_file):
        self.path_to_file = path_to_file
        self.__errors = []
        self.__checks = []
        self.__prepare_checks()

    def perform_checks(self):
        with open(self.path_to_file) as fh:
            for ln, l in enumerate(fh.readlines(), 1):
                for m in self.__checks:
                    m(l)

    def check_line_length(self, line: str):
        print('line')

    def check_indentation(self, line: str):
        print('indentation')

    def check_semicolon(self, line: str):
        print('semi')

    def check_spaces(self, line: str):
        print('spaces')

    def check_todo(self, line: str):
        print('TODO')

    def check_blank_lines(self, line: str):
        print('Blank lines')

    def __prepare_checks(self):
        for mn in self.__dir__():
            if mn.startswith('check_'):
                m = getattr(self, mn)
                if callable(m):
                    self.__checks.append(m)

    def get_errors(self):
        return self.__errors


def main():
    code_analyzed = CodeAnalyzer(input())
    code_analyzed.perform_checks()
    print(code_analyzed.get_errors())


if __name__ == '__main__':
    main()
