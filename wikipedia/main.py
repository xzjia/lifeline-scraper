from requests_html import HTMLSession
from wiki import Wikipedia


def main():
    wikipedia = Wikipedia(store_json=True)


if __name__ == '__main__':
    main()
