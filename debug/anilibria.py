#!/usr/bin/env python3

import json
import requests
import re


API_RELEASES_URL='https://aniliberty.top/api/v1/anime/releases/{}'
API_PARAMS={
    'include': ['torrents'],
    'exclude': ['torrents.release']
}

TEMPLATE_URL='https://gist.githubusercontent.com/Victor-Y-Fadeev/6b804186461c3d4272c0eea53e9546f5/raw/{}'
ANILIBRIA_URL=TEMPLATE_URL.format('anilibria.md')
ANILIBERTY_URL=TEMPLATE_URL.format('aniliberty.md')
GIST_URL=ANILIBRIA_URL


def save_json(path: str, obj):
    with open(path, 'w', encoding='utf-8') as file:
        file.write(json.dumps(obj, indent=4))


def load_json(path: str):
    with open(path, 'r', encoding='utf-8') as file:
        return json.loads(file.read())


def release_links_from_gist(url: str) -> list[str]:
    response = requests.get(url)
    gist = response.text
    links = re.findall(r'https?://.*/release/[^\s\(\)]+', gist)
    return list(links)


def links_to_aliases(links: list[str]) -> list[str]:
    for link in links:
        yield re.search(r'/release/([^\./]+)', link).group(1)


def api_releases(alias: str):
    response = requests.get(API_RELEASES_URL.format(alias),
                            params=API_PARAMS)
    return response.json() if response.ok else response.status_code


def aliases_to_releases(aliases: list[str]) -> dict:
    releases = dict()
    for alias in aliases:
        releases[alias] = api_releases(alias)
    return releases


def main():
    # links = release_links_from_gist(GIST_URL)
    # save_json('links.json', links)
    # links = load_json('links.json')

    # aliases = list(links_to_aliases(links))
    # save_json('aliases.json', aliases)
    aliases = load_json('aliases.json')

    releases = aliases_to_releases(aliases)
    save_json('releases.json', releases)
    releases = load_json('releases.json')


if __name__ == '__main__':
    main()
