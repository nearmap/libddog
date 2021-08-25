# libddog user guide


## How to get started

The easiest way to get started with libddog is to use the [example skeleton project](skel) as a starting point:

```bash
$ git clone https://github.com/nearmap/libddog /tmp/libddog
$ cp -r /tmp/libddog/docs/skel monitoring-project
$ cd monitoring-project
$ git init
```

You will need to install libddog on your system. Using a [virtualenv](https://virtualenv.pypa.io/en/latest/) and [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) are highly recommended. We will assume you are using `virtualenvwrapper`:

```bash
$ mkvirtualenv monitoring-project
(monitoring-project) $ pip install -r requirements.txt 
Successfully installed libddog-0.0 ...snip...
```

You can now use the `ddog` command line tool to manage your dashboards. To list the dashboards defined in the project:

```bash
(monitoring-project) $ ddog dash list-defs
ID           GROUPS  WIDGETS  QUERIES  TITLE
None              0        1        1  libddog skel: AWS EC2 dashboard
```

There are also some helpful scripts in the `ci/` directory to run `black` (code formatter) and `mypy` (static type checker) on your project. To get these working first install the development tools:

```bash
(monitoring-project) $ pip install -r dev-requirements.txt 
```

libddog uses type annotations and we highly recommend that you take advantage of them to keep your code working correctly. A clean slate execution will say:

```bash
(monitoring-project) $ ci/typecheck 
Success: no issues found in 5 source files
```