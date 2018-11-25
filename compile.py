#! encoding: utf-8
import os
import re
import shutil
import markdown2
import pyphen
from jinja2 import FileSystemLoader, Environment 


LANGUAGES = [
    {
        'lang': 'en',
        'title': '101 Zen Stories',
        'local': 'english',
        'prev': 'previous',
        'next': 'next',
        'toc': 'toc',
    },
    {
        'lang': 'ru',
        'title': '101 дзенская история',
        'local': 'русский',
        'prev': 'предыдущая',
        'next': 'следующая',
        'toc': 'оглавление',
    },
    {
        'lang': 'pl',
        'title': '101 opowieści zen',
        'local': 'polski',
        'prev': 'poprzednia',
        'next': 'kolejna',
        'toc': 'spis treści',
    },
]


ROOT_URL = '/zen101' if os.getenv('GITHUB') else ''


basedir = os.path.dirname(os.path.realpath(__file__))
loader = FileSystemLoader(os.path.join(basedir, 'templates'))
env = Environment(loader=loader, lstrip_blocks=True, trim_blocks=True)


def main():
    out = os.path.join(basedir, 'output')
    if os.path.exists(out):
        for n in os.listdir(out):
            out_file = os.path.join(out, n)
            if os.path.isfile(out_file):
                os.unlink(out_file)
            else:
                shutil.rmtree(out_file)
    else:
        os.mkdir(out)

    shutil.copytree(os.path.join(basedir, 'static'), 
                    os.path.join(basedir, 'output', 'static'))

    story_template = env.get_template('story.html')
    index_template = env.get_template('index.html')
    toc_template = env.get_template('toc.html')

    markdowner = markdown2.Markdown(extras=['smarty-pants', 'break-on-newline'])

    with open(os.path.join(out, 'index.html'), 'w') as f:
        params = {
            'root': ROOT_URL,
            'title': '禪',
            'langs': LANGUAGES,
        }
        f.write(index_template.render(**params))

    for metadata in LANGUAGES:
        lang = metadata['lang']
        dic = pyphen.Pyphen(lang=lang)
        in_dir = os.path.join(basedir, 'content', lang)
        out_dir = os.path.join(basedir, 'output', lang)
        os.mkdir(out_dir)

        def insert_hyphens(match):
            word = match.group()
            if word[0].isupper():
                return word
            return dic.inserted(word, '&shy;')

        pages = []
        for filename in (f for f in os.listdir(in_dir) if f.endswith('.md')):
            with open(os.path.join(in_dir, filename)) as f:
                content = f.read()

            title = re.match('# (.+)', content).groups()[0]
            num = re.match('(\d+)', filename).groups()[0]

            content = markdowner.convert(content)
            content = re.sub(r'\w+', insert_hyphens, content)

            page_out_dir = os.path.join(out_dir, num)
            page_out_file = os.path.join(page_out_dir, 'index.html')

            pages.append({
                'title': title,
                'num': int(num),
                'content': content,
                'href': ROOT_URL + '/{}/{}/'.format(lang, num),
                'out_dir': page_out_dir,
                'out_file': page_out_file
            })

        pages = sorted(pages, key=lambda p: p['num'])
        for i, page in enumerate(pages):
            page = pages[i]
            prev = next = None
            if i > 0:
                prev = pages[i - 1]['href']
            if i < len(pages) - 1:
                next = pages[i + 1]['href']

            os.mkdir(page['out_dir'])
            with open(page['out_file'], 'w') as f:
                params = {
                    'root': ROOT_URL,
                    'text': metadata,
                    'title': page['title'],
                    'content': page['content'],
                    'prev': prev,
                    'next': next,
                    'toc': ROOT_URL + '/{}/'.format(lang),
                }
                f.write(story_template.render(**params))

        with open(os.path.join(out_dir, 'index.html'), 'w') as f:
            params = {
                'root': ROOT_URL,
                'title': metadata['title'],
                'pages': pages,
            }
            f.write(toc_template.render(**params))


if __name__ == '__main__':
    main()
