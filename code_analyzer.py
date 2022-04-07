def main():
    path_to_file = input()

    with open(path_to_file) as fh:
        for ln, l in enumerate(fh.readlines(), 1):
            if len(l) > 79:
                print(f'Line {ln}: S001 Too long')


if __name__ == '__main__':
    main()