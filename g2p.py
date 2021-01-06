import json
from pathlib import Path
from subprocess import Popen, PIPE, DEVNULL
from tempfile import NamedTemporaryFile

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, abort

from settings import config

g2p_page = Blueprint('g2p_page', __name__)


@g2p_page.route('/')
def g2p_index():
    vocab_path = config['data'] / 'vocab'
    vocab_files = sorted(list(vocab_path.glob('*.json')))
    lex_path = config['data'] / 'lex'
    lex_files = sorted(list(lex_path.glob('*.json')))
    model_path = config['data'] / 'model'
    model_files = sorted(list(model_path.glob('*.fst')))
    return render_template('g2p_index.html', vocab_files=vocab_files, lex_files=lex_files, model_files=model_files)


@g2p_page.route('/wordlist', methods=['post'])
def g2p_wlist():
    name = request.form.get('name')
    lex_path = config['data'] / 'lex' / (name + '.json')
    vocab_file = config['data'] / 'vocab' / (request.form.get('vocab') + '.json')
    model_file = config['data'] / 'model' / (request.form.get('model') + '.fst')
    cache_file = None
    if request.form.get('cache'):
        cache_file = config['data'] / 'lex' / (request.form.get('cache') + '.json')
    nbest = int(request.form.get('nbest'))
    pmass = float(request.form.get('pmass'))
    beam = int(request.form.get('beam'))

    with open(str(vocab_file)) as f:
        data = json.load(f)

    lex = []
    cached_words = set()

    if cache_file:
        with open(str(cache_file)) as f:
            lex = json.load(f)
        for w in lex:
            cached_words.add(w['w'])

    with NamedTemporaryFile('w', delete=False) as g:
        wlist_file = Path(g.name)
        for w in data:
            if w not in cached_words:
                g.write(w + '\n')

    cmd = [f'{config["phonetisaurus_bin"]}/phonetisaurus-g2pfst', f'--model={model_file}',
           f'--nbest={nbest}', f'--pmass={pmass}', f'--beam={beam}', f'--wordlist={wlist_file}']

    tmplex = {}
    proc = Popen(cmd, stdout=PIPE, stderr=DEVNULL, text=True)
    for l in proc.stdout:
        tok = l.strip().split()
        word = tok[0]
        trans = tok[2:]
        if word not in lex:
            tmplex[word] = []
        tmplex[word].append(trans)

    wlist_file.unlink()

    lex.extend([{'w': w, 't': t} for w, t in tmplex.items()])

    with open(str(lex_path), 'w') as f:
        json.dump(lex, f)

    return redirect(url_for('lex_page.lex_index'))


@g2p_page.route('/words', methods=['post'])
def g2p_words():
    words = request.form.get('words')
    model_file = config['data'] / 'model' / (request.form.get('model') + '.fst')
    nbest = int(request.form.get('nbest'))
    pmass = float(request.form.get('pmass'))
    beam = int(request.form.get('beam'))
    type = request.form.get('output')

    with NamedTemporaryFile('w', delete=False) as g:
        wlist_file = Path(g.name)
        for w in words.splitlines():
            g.write(w + '\n')

    cmd = [f'{config["phonetisaurus_bin"]}/phonetisaurus-g2pfst', f'--model={model_file}',
           f'--nbest={nbest}', f'--pmass={pmass}', f'--beam={beam}', f'--wordlist={wlist_file}']

    lex = {}
    proc = Popen(cmd, stdout=PIPE, stderr=DEVNULL, text=True)
    for l in proc.stdout:
        tok = l.strip().split()
        word = tok[0]
        trans = tok[2:]
        if word not in lex:
            lex[word] = []
        lex[word].append(trans)

    wlist_file.unlink()

    lex = [{'w': w, 't': t} for w, t in lex.items()]

    if type == 'json':
        return jsonify(lex)
    elif type == 'text':
        ret = ''
        for w in lex:
            for t in w['t']:
                ret += f'{w["w"]}\t{" ".join(t)}\n'
        return ret
    elif type == 'html':
        ret="<style>table,td{border:1px solid black;border-collapse:collapse;padding:0.5em}</style>"
        ret += '<table>'
        for w in lex:
            if len(w['t']) > 1:
                ret += '<tr>'
                ret += f'<td rowspan="{len(w["t"])}">{w["w"]}</td>'
                ret += f'<td>{" ".join(w["t"][0])}</td>'
                ret += '</tr>'
                for t in w['t'][1:]:
                    ret += '<tr>'
                    ret += f'<td>{" ".join(t)}</td>'
                    ret += '</tr>'

            else:
                ret += '<tr>'
                ret += f'<td>{w["w"]}</td>'
                ret += f'<td>{" ".join(w["t"][0])}</td>'
                ret += '</tr>'
        ret += '</table>'
        return ret
    else:
        return abort(304, description=f'Output type unknown: {type}')
