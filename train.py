from pathlib import Path
from subprocess import run, DEVNULL
from tempfile import NamedTemporaryFile

from flask import Blueprint, render_template, request, redirect, send_file
from werkzeug.utils import secure_filename

from lex import lex_generator
from settings import config

train_page = Blueprint('train_page', __name__)


@train_page.route('/', methods=['GET', 'POST'])
def train_index():
    if request.method == 'GET':
        lex_path = config['data'] / 'lex'
        lex_files = sorted(list(lex_path.glob('*.json')))
        model_path = config['data'] / 'model'
        model_files = sorted(list(model_path.glob('*.fst')))
        return render_template('train_index.html', lex_files=lex_files, model_files=model_files)
    else:

        model_path = config['data'] / 'model' / (request.form.get('name') + '.fst')
        lex_path = config['data'] / 'lex' / (request.form.get('lex') + '.json')

        with NamedTemporaryFile('w', delete=False) as f:
            for l in lex_generator(lex_path):
                f.write(l)
            lex_path = Path(f.name)

        with NamedTemporaryFile('w', delete=False) as f:
            ali_path = Path(f.name)

        cmd = [str(config['phonetisaurus_bin'] / 'phonetisaurus-align'), f'--input={lex_path}', f'--ofile={ali_path}']
        run(cmd, stderr=DEVNULL)

        with NamedTemporaryFile('w', delete=False) as f:
            ngram_path = Path(f.name)

        cmd = [str(config['srilm_bin'] / 'ngram-count'), '-text', str(ali_path), '-lm', str(ngram_path), '-order', '3',
               '-wbdiscount']
        run(cmd, stderr=DEVNULL)

        cmd = [str(config['phonetisaurus_bin'] / 'phonetisaurus-arpa2wfst'), f'--lm={ngram_path}',
               f'--ofile={model_path}']
        run(cmd, stderr=DEVNULL)

        lex_path.unlink()
        ali_path.unlink()
        ngram_path.unlink()

        return redirect('/g2p')


@train_page.route('get/<model>')
def model_get(model):
    model_path = config['data'] / 'model' / (model + '.fst')
    return send_file(model_path)


@train_page.route('delete/<model>')
def model_delete(model):
    model_path = config['data'] / 'model' / (model + '.fst')
    model_path.unlink(missing_ok=True)
    return redirect('train_page.train_index')


@train_page.route('add', methods=['post'])
def model_add():
    name = secure_filename(request.form.get('name'))
    model_path = config['data'] / 'model' / (name + '.fst')

    file = request.files['file']

    file.save(str(model_path))

    return redirect('train_page.train_index')
