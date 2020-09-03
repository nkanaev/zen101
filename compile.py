#! coding: utf-8
import os
import re
import shutil
import markdown2
import misai

BASEDIR = os.path.dirname(os.path.realpath(__file__))

LANGUAGES = [
    {'en': '101 Zen Stories'},
    {'it': '101 дзенская история'},
    {'ru': '101 opowieści zen'},
    {'pl': '101 historia zen'}
]


@misai.filter
def indent(content, num):
    return re.sub('\n', '\n' + ' ' * num, str(content), flags=re.M)


def main():
    path = lambda *pathnames: os.path.join(BASEDIR, *pathnames)
    read = lambda filepath: open(filepath).read()
    dump = lambda filepath, content: open(filepath, 'w').write(content)

    outdir = path('output')
    if os.path.exists(outdir):
        shutil.rmtree(outdir)

    template = misai.Template(open(path('assets', 'base.html')).read())
    markdown = markdown2.Markdown(extras=['smarty-pants', 'break-on-newline'])

    allstories = {}
    for lang in LANGUAGES:
        stories = []
        for num in range(1, 102):
            body = read(path('stories', lang, '%03d.md' % num))
            body = markdown.convert(body)
            body = re.sub('\n\n', '\n', body).strip()

            stories.append({
                'title': re.match('<h1>(.+?)</h1>', body).groups()[0],
                'body': body,
                'href': './{l}/{n}/'.format(l=lang, n=num),
                'filepath': path('output', lang, num, 'index.html')
            })
        allstories[lang] = stories

    for static in ['enso.svg', 'favicon.ico', 'styles.css']:
        shutil.copy(path('assets', static), path('output'))

    # dump: index
    params = {'page': 'index', 'title': '禪', 'langs': LANGUAGES, 'root': '.'}
    dump(path('output', 'index.html'), template.render(**params))

    # dump: toc & stories
    for lang, stories in allstories:
        for s in stories:
            params = {'lang': lang, 'page': 'story', 'title': s['title'], 'body': s['body'], 'root': './..'}
            dump(s['filepath'], template.render(**params))

        params = {'lang': lang, 'page': 'toc', 'title': LANGUAGES[lang], 'stories': stories, 'root': '.'}
        dump(path('output', lang, 'index.html'), template.render(**params))


if __name__ == '__main__':
    main()
