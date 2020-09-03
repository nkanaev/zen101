#! coding: utf-8
import os
import re
import shutil
import markdown2
import misai

BASEDIR = os.path.dirname(os.path.realpath(__file__))

LANGUAGES = {
    'en': '101 Zen Stories',
    'it': '101 Дзенская История',
    'ru': '101 Opowieści Zen',
    'pl': '101 Historia Zen',
}


@misai.filter
def indent(content, num):
    return re.sub('\n', '\n' + ' ' * num, str(content), flags=re.M)


def main():
    path = lambda *pathnames: os.path.join(BASEDIR, *pathnames)
    read = lambda filepath: open(filepath).read()
    dump = lambda filepath, content: open(filepath, 'w').write(content)

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
                'title': misai.noescapestr(re.match('<h1>(.+?)</h1>', body).groups()[0]),
                'body': body,
                'num': num,
            })
        allstories[lang] = stories

    outdir = path('output')
    if os.path.isdir(outdir):
        shutil.rmtree(outdir)
    os.mkdir(outdir)

    for static in ['favicon.ico', 'styles.css']:
        shutil.copy(path('assets', static), path('output', static))

    # dump: index
    params = {'page': 'index', 'lang': '', 'title': '禪', 'langs': LANGUAGES, 'root': '.'}
    dump(path('output', 'index.html'), template.render(**params))

    # dump: toc & stories
    for lang, stories in allstories.items():
        os.mkdir(path('output', lang))
        for s in stories:
            num = s['num']
            os.mkdir(path('output', lang, '%03d' % num))
            s['href'] = './{n}/'.format(n='%03d' % num)
            params = {
                'page': 'story', 'lang': lang, 'root': '../..',
                'title': s['title'], 'body': s['body'],
            }
            dump(path('output', lang, '%03d' % num, 'index.html'), template.render(**params))

        params = {'page': 'toc', 'lang': lang, 'title': LANGUAGES[lang], 'stories': stories, 'root': '..'}
        dump(path('output', lang, 'index.html'), template.render(**params))


if __name__ == '__main__':
    main()
