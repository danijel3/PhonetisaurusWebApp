# Phonetisaurus G2P model development web app

This is a Python/Flask project that serves as a simple GUI to develop and test Phonetisaurus
models. 

The Phonetisaurus project is available under https://github.com/AdolfVonKleist/Phonetisaurus
It is a very popular G2P tool used (among others) in Kaldi. Another popular alternative is [Sequitur G2P](https://www-i6.informatik.rwth-aachen.de/web/Software/g2p.html). 


The following features are included in the current version of the web app:

* upload/view/edit word lists
* upload/view/edit G2P lexica
* upload/delete/download G2P models 
* generate lexica from word lists
* train G2P models from lexica
* test G2P models

Some features missing/under development:

* only FST models, for now
* only SRILM used for training
* simplistic file management (no checks for duplicats/security)
* no access control (no users/passwords)
* missing collaboration tools (many people working at the same time)

## Usage

If you have Docker, simply run:

```bash
docker run --rm -it -p 80:80 danijel3/phonetisaurus-web-app
```

This will run (interactively) an instance of the server on port 80 on localhost. Simply open `http://localhost` in your browser and start using.

For a slightly more permenant solution, docker-compose is recommended. Copy the `docker-compose.yml` to a server
of your choice and create the `data` subdirectory:

```bash
mkdir -p data/model data/lex data/vocab
```

Edit the `docker-compose.yml` file if necessary and run:

```bash
docker-compose up -d
```

This will keep the server up indefinitely.

## Build

The image is built automatically by DockerHub here:
https://hub.docker.com/repository/docker/danijel3/phonetisaurus-web-app