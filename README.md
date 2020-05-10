
pip install -r dev-requirements.txt
pip install -e .

External requirements:
  * libvips - $ apt install libvips-tools
  * exiftool - $ apt install libimage-exiftool-perl

Make migrations:

    $ ./manage.py makemigrations vgloss

Development setup. Run Django dev server on port 8000. Run webpack server on
port 8001, forwarding non-js requests to port 8000. Go to port 8001 to develop
JS:

    $ VGLOSS_BASE=test1/ vgloss serve
    $ yarn run serve --port 8001 --hot

Folder SVG taken from: https://www.svgrepo.com/svg/97469/folder

# vglossjs

## Project setup
```
yarn install
```

### Compiles and hot-reloads for development
```
yarn serve
```

### Compiles and minifies for production
```
yarn build
```

### Lints and fixes files
```
yarn lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
