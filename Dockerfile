FROM python:3 as build

WORKDIR /build

RUN apt-get -y update && apt-get -y install git g++ autoconf-archive make libtool gfortran tar

RUN wget http://www.openfst.org/twiki/pub/FST/FstDownload/openfst-1.6.2.tar.gz && \
    tar -xvzf openfst-1.6.2.tar.gz && \
    cd openfst-1.6.2 && \
    ./configure --enable-static --enable-shared --enable-far --enable-ngram-fsts && \
    make -j $(nproc) && \
    make install && \
    ldconfig

RUN git clone https://github.com/AdolfVonKleist/Phonetisaurus.git && \
    cd Phonetisaurus && \
    ./configure && \
    make -j $(nproc)&& \
    make install

RUN wget https://github.com/downloads/chokkan/liblbfgs/liblbfgs-1.10.tar.gz && \
    tar xvf liblbfgs-1.10.tar.gz && \
    cd liblbfgs-1.10 && \
    ./configure && \
    make -j $(nproc) && \
    make -i install && \
    ldconfig

ADD https://github.com/danijel3/PhonetisaurusWebApp/releases/download/srilm/srilm.tgz ./srilm/

RUN  apt-get -y install gawk

RUN cd ./srilm/ && cp Makefile tmpf && \
    cat tmpf | awk -v pwd=`pwd` '/SRILM =/{printf("SRILM = %s\n", pwd); next;} {print;}' > Makefile && \
    mtype=$(sbin/machine-type) && \
    echo HAVE_LIBLBFGS=1 >> common/Makefile.machine.$mtype && \
    make -j $(nproc)

FROM python:3

ADD requirements.txt /tmp/

RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app

RUN mkdir -p data/lex data/model data/vocab

ADD static ./static
ADD templates ./templates
ADD *.py ./

ADD data/model/clarin.fst data/model/

COPY --from=build /usr/local/lib/fst /usr/local/lib/fst
COPY --from=build /usr/local/lib/libfst*so*0 /usr/local/lib/
COPY --from=build /usr/local/lib/liblbfgs-1.10.so /usr/local/lib/
COPY --from=build /usr/local/bin/phonetisaurus-align /usr/local/bin/
COPY --from=build /usr/local/bin/phonetisaurus-arpa2wfst /usr/local/bin/
COPY --from=build /usr/local/bin/phonetisaurus-g2pfst /usr/local/bin/
COPY --from=build /build/srilm/bin/i686-m64/ngram-count /usr/local/bin/

RUN ldconfig

EXPOSE 80

CMD gunicorn --bind 0.0.0.0:80 --timeout=1800 --workers=4 --threads=4 --max-requests=30 --max-requests-jitter=20 --name=gunicorn  main