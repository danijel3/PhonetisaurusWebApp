from pathlib import Path

config = {'data': Path(__file__).parent / 'data',
          'phonetisaurus_bin': Path('/opt/kaldi/tools/phonetisaurus-g2p'),
          'srilm_bin': Path('/opt/kaldi/tools/srilm/bin/i686-m64')}
