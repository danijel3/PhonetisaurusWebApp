import json

from flask import Blueprint, render_template, request, app, send_file, jsonify, Response, redirect, url_for, abort

from settings import config

vocab_page = Blueprint('vocab_page', __name__)


@vocab_page.route('/')
def vocab_index():
    vocab_path = config['data'] / 'vocab'
    files = sorted(list(vocab_path.glob('*.json')))
    return render_template('vocab_index.html', files=files)


@vocab_page.route('/view/<file>')
def vocab_view(file):
    return render_template('vocab_view.html', file=file)


@vocab_page.route('/get/<file>')
def vocab_get(file):
    file_path = config['data'] / 'vocab' / (file + '.json')

    def generator(path):
        with open(path) as f:
            data = json.load(f)
            for word in data:
                yield word + '\n'

    return Response(generator(file_path),
                    mimetype='text/plain',
                    headers={'Content-Disposition': f'attachment;filename={file}.txt'})


@vocab_page.route('/view/src/<file>')
def vocab_viewsrc(file):
    vocab_path = config['data'] / 'vocab'
    return send_file(vocab_path / (file + '.json'), cache_timeout=-1)


@vocab_page.route('/write/<file>', methods=['post'])
def vocab_write(file):
    data = json.loads(request.get_data())
    vocab_path = config['data'] / 'vocab' / (file + '.json')
    data = sorted(list(set(data)))
    with open(str(vocab_path), 'w') as f:
        json.dump(data, f)
    return jsonify(success=True)


@vocab_page.route('/add', methods=['get', 'post'])
def vocab_add():
    if request.method == 'GET':
        return render_template('vocab_add.html')
    else:
        name = request.form.get('name')
        file = request.files['file']
        filetype = request.form.get('filetype')

        vocab_path = config['data'] / 'vocab' / (name + '.json')

        dict = set()

        if file.filename:
            if filetype == 'wordlist':
                for l in file:
                    dict.add(l.decode('utf-8').strip())
            elif filetype == 'text':
                for l in file:
                    tok = l.decode('utf-8').strip().split()
                    for w in tok:
                        dict.add(w)
            else:
                abort(403, description=f'Unknown filetype: {filetype}')

        dict = sorted(list(dict))
        with open(str(vocab_path), 'w') as f:
            json.dump(dict, f)

        return redirect(url_for('vocab_page.vocab_index'))


@vocab_page.route('/del/<file>')
def vocab_del(file):
    vocab_path = config['data'] / 'vocab'
    file_path = vocab_path / (file + '.json')
    if file_path.parent != vocab_path:
        abort(403)
    file_path.unlink(missing_ok=True)
    return redirect(url_for('vocab_page.vocab_index'))
