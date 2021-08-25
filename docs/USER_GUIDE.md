# libddog user guide


## How to get started

The easiest way to get started with libddog is to use the [example skeleton project](skel) as a starting point:

```bash
$ git clone https://github.com/nearmap/libddog /tmp/libddog
$ cp -r /tmp/libddog/docs/skel monitoring-project
$ cd monitoring-project
```

You will need to install libddog on your system. Using a [virtualenv](https://virtualenv.pypa.io/en/latest/) and [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) are highly recommended. We will assume you are using `virtualenvwrapper`:

```bash
$ mkvirtualenv monitoring-project
(monitoring-project) $ pip install -r requirements.txt 
```