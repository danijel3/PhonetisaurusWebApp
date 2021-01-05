import json

from flask import Blueprint, render_template, send_file, Response, request, jsonify, abort, redirect, url_for

from settings import config

lex_page = Blueprint('lex_page', __name__)


@lex_page.route('/')
def lex_index():
    lex_path = config['data'] / 'lex'
    files = sorted(list(lex_path.glob('*.json')))
    return render_template('lex_index.html', files=files)


@lex_page.route('/view/<file>')
def lex_view(file):
    return render_template('lex_view.html', file=file)


@lex_page.route('/view/src/<file>')
def lex_viewsrc(file):
    lex_path = config['data'] / 'lex'
    return send_file(lex_path / (file + '.json'), cache_timeout=-1)


def lex_generator(path):
    with open(path) as f:
        data = json.load(f)
        for word in data:
            for trans in word['t']:
                yield f'{word["w"]}\t{" ".join(trans)}\n'

@lex_page.route('/get/<file>')
def lex_get(file):
    file_path = config['data'] / 'lex' / (file + '.json')

    return Response(lex_generator(file_path),
                    mimetype='text/plain',
                    headers={'Content-Disposition': f'attachment;filename={file}.txt'})


@lex_page.route('/write/<file>', methods=['post'])
def lex_write(file):
    data = json.loads(request.get_data())
    lex_path = config['data'] / 'lex' / (file + '.json')
    with open(str(lex_path), 'w') as f:
        json.dump(data, f)
    return jsonify(success=True)


@lex_page.route('/add', methods=['get', 'post'])
def lex_add():
    if request.method == 'GET':
        return render_template('lex_add.html')
    else:
        name = request.form.get('name')
        lex_path = config['data'] / 'lex' / (name + '.json')

        file = request.files['file']

        lex = {}

        if file.filename:
            for l in file:
                tok = l.decode('utf-8').strip().split()
                word = tok[0]
                trans = tok[1:]
                if word not in lex:
                    lex[word] = []
                lex[word].append(trans)

        lex = [{'w': w, 't': t} for w, t in lex.items()]

        with open(str(lex_path), 'w') as f:
            json.dump(lex, f)

        return redirect(url_for('lex_page.lex_index'))


@lex_page.route('/del/<file>')
def lex_del(file):
    lex_path = config['data'] / 'lex'
    file_path = lex_path / (file + '.json')
    if file_path.parent != lex_path:
        abort(403)
    file_path.unlink(missing_ok=True)
    return redirect(url_for('lex_page.lex_index'))
