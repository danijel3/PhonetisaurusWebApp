from flask import Flask, render_template

from g2p import g2p_page
from lex import lex_page
from train import train_page
from vocab import vocab_page

application = Flask('PhonetisaurusWebApp')

application.register_blueprint(vocab_page, url_prefix='/vocab/')
application.register_blueprint(lex_page, url_prefix='/lex/')
application.register_blueprint(g2p_page, url_prefix='/g2p/')
application.register_blueprint(train_page, url_prefix='/train/')


@application.route('/')
def index():
    return render_template('index.html')
