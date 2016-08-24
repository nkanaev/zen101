#! encoding: utf-8
from __future__ import unicode_literals
import os
import re
import shutil
import markdown2
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
        'prev': 'предыдущий',
        'next': 'следующий',
        'toc': 'оглавление',
    },
]


ROOT_URL = '/zen101' if os.getenv('GITHUB') else ''


basedir = os.path.dirname(os.path.realpath(__file__))
loader = FileSystemLoader(os.path.join(basedir, 'templates'))
env = Environment(loader=loader)


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

    page_template = env.get_template('page.html')
    main_template = env.get_template('main.html')
    index_template = env.get_template('index.html')

    markdowner = markdown2.Markdown(extras=['smarty-pants'])

    with open(os.path.join(out, 'index.html'), 'w') as f:
        params = {
            'root': ROOT_URL,
            'title': '禪',
            'langs': LANGUAGES,
        }
        f.write(main_template.render(**params).encode('utf-8'))

    for metadata in LANGUAGES:
        lang = metadata['lang']
        in_dir = os.path.join(basedir, 'content', lang)
        out_dir = os.path.join(basedir, 'output', lang)
        os.mkdir(out_dir)

        pages = []
        for filename in (f for f in os.listdir(in_dir) if f.endswith('.md')):
            with open(os.path.join(in_dir, filename)) as f:
                content = f.read().decode('utf-8')

            title = re.match('# (.+)', content).groups()[0]
            num = re.match('(\d+)', filename).groups()[0]

            page_out_dir = os.path.join(out_dir, num)
            page_out_file = os.path.join(page_out_dir, 'index.html')

            pages.append({
                'title': title,
                'num': num,
                'content': markdowner.convert(content),
                'href': ROOT_URL + '/{}/{}/'.format(lang, num),
                'out_dir': page_out_dir,
                'out_file': page_out_file
            })

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
                f.write(page_template.render(**params).encode('utf-8'))

        with open(os.path.join(out_dir, 'index.html'), 'w') as f:
            params = {
                'root': ROOT_URL,
                'title': metadata['title'],
                'pages': pages,
            }
            f.write(index_template.render(**params).encode('utf-8'))


if __name__ == '__main__':
    main()
