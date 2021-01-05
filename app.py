from flask import Flask, render_template

from g2p import g2p_page
from lex import lex_page
from settings import config
from train import train_page
from vocab import vocab_page

app = Flask('PhonetisaurusWebApp')

app.register_blueprint(vocab_page, url_prefix='/vocab/')
app.register_blueprint(lex_page, url_prefix='/lex/')
app.register_blueprint(g2p_page, url_prefix='/g2p/')
app.register_blueprint(train_page, url_prefix='/train/')


@app.route('/')
def index():
    return render_template('index.html')
