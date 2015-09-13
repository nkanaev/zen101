#! encoding: utf-8
import os
import re
import shutil
import markdown
from jinja2 import FileSystemLoader, Environment 


LANGUAGES = {
        'en': {'title': u'101 Zen Stories', 'local': u'english'},
        'ru': {'title': u'101 дзенская история', 'local': u'русский'},
}


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

    main = env.get_template('main.html')
    with open(os.path.join(out, 'index.html'), 'w') as f:
        params = {
            'title': 'o',
            'langs': LANGUAGES,        
        }
        f.write(main.render(**params).encode('utf-8'))

    for lang, metadata in LANGUAGES.items():
        titles = []
        in_dir = os.path.join(basedir, 'content', lang)
        out_dir = os.path.join(basedir, 'output', lang)
        os.mkdir(out_dir)
        page = env.get_template('page.html')
        for filename in os.listdir(in_dir):
            with open(os.path.join(in_dir, filename)) as f:
                content = f.read().decode('utf-8')

            out_file = re.sub(r'\.md', '.html', filename)
            title = re.match('# (.+)', content).groups()[0]
            with open(os.path.join(out_dir, out_file), 'w') as f:
                params = {
                    'title': title,
                    'content': markdown.markdown(content),
                }
                f.write(page.render(**params).encode('utf-8'))            

            titles.append({
                'name': title, 
                'href': out_file
            })

        index = env.get_template('index.html')
        with open(os.path.join(out_dir, 'index.html'), 'w') as f:
            params = {
                'title': metadata['title'],
                'titles': titles,
            }
            f.write(index.render(**params).encode('utf-8'))


if __name__ == '__main__':
    main()
