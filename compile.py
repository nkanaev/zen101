#! encoding: utf-8
import os
import re
import shutil
import markdown2
import misai


ROOT_URL = '/zen101' if os.getenv('GITHUB') else ''

LANGUAGES = [
    {
        'lang': 'en',
        'title': '101 Zen Stories',
        'local': 'english',
    },
    {
        'lang': 'ru',
        'title': '101 дзенская история',
        'local': 'русский',
    },
    {
        'lang': 'pl',
        'title': '101 opowieści zen',
        'local': 'polski',
    },
    {
        'lang': 'it',
        'title': '101 historia zen',
        'local': 'italiano',
    }
]


BASEDIR = os.path.dirname(os.path.realpath(__file__))

x = 0

@misai.filter
def indent(content, num):
    return re.sub('\n', '\n' + ' ' * num, str(content), flags=re.M)


def main():
    out = os.path.join(BASEDIR, 'output')
    if os.path.exists(out):
        for n in os.listdir(out):
            out_file = os.path.join(out, n)
            if os.path.isfile(out_file):
                os.unlink(out_file)
            else:
                shutil.rmtree(out_file)
    else:
        os.mkdir(out)

    shutil.copytree(
        os.path.join(BASEDIR, 'static'), os.path.join(BASEDIR, 'output', 'static'))

    loader = misai.Loader(
        basedir=os.path.join(BASEDIR, 'templates'),
        locals={'root': ROOT_URL})
    story_template = loader.get('story.html')
    index_template = loader.get('index.html')
    toc_template = loader.get('toc.html')

    markdowner = markdown2.Markdown(extras=['smarty-pants', 'break-on-newline'])

    with open(os.path.join(out, 'index.html'), 'w') as f:
        params = {
            'title': '禪',
            'langs': LANGUAGES,
        }
        f.write(index_template.render(**params))

    for metadata in LANGUAGES:
        lang = metadata['lang']
        in_dir = os.path.join(BASEDIR, 'content', lang)
        out_dir = os.path.join(BASEDIR, 'output', lang)
        os.mkdir(out_dir)

        pages = []
        for filename in (f for f in os.listdir(in_dir) if f.endswith('.md')):
            with open(os.path.join(in_dir, filename)) as f:
                content = f.read()

            title = re.match('# (.+)', content).groups()[0]
            num = re.match('(\d+)', filename).groups()[0]

            content = markdowner.convert(content)
            content = re.sub('\n\n', '\n', content).strip()

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
                    'lang': lang,
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
                'title': metadata['title'],
                'pages': pages,
                'lang': lang,
            }
            f.write(toc_template.render(**params))


if __name__ == '__main__':
    main()
