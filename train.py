from pathlib import Path
from subprocess import run, DEVNULL
from tempfile import NamedTemporaryFile

from flask import Blueprint, render_template, request, redirect

from lex import lex_generator
from settings import config

train_page = Blueprint('train_page', __name__)


@train_page.route('/', methods=['GET', 'POST'])
def train_index():
    if request.method == 'GET':
        lex_path = config['data'] / 'lex'
        lex_files = sorted(list(lex_path.glob('*.json')))
        return render_template('train_index.html', lex_files=lex_files)
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
        run(cmd)

        cmd = [str(config['phonetisaurus_bin'] / 'phonetisaurus-arpa2wfst'), f'--lm={ngram_path}',
               f'--ofile={model_path}']
        run(cmd)

        lex_path.unlink()
        ali_path.unlink()
        ngram_path.unlink()

        return redirect('/g2p')
