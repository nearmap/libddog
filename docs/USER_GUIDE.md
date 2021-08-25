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
Successfully installed libddog-0.0.1 ...snip...
```

You can now use the `ddog` command line tool to manage your dashboards. To list the dashboards defined in the project:

```bash
(monitoring-project) $ ddog dash list-defs
ID           GROUPS  WIDGETS  QUERIES  TITLE
None              0        1        1  libddog skel: AWS ELB dashboard
```



## Datadog credentials

The `ddog` tool communicates with the Datadog API and this requires valid credentials:
1) An API key which is specific to your organization. You can create one [on this page](https://app.datadoghq.com/account/settings#api).
2) An application key which is specific to your user account. You can create one [on this page](https://app.datadoghq.com/access/application-keys).

These two keys need to be set in your environment:

```bash
export DATADOG_API_KEY=...
export DATADOG_APPLICATION_KEY=...
```



## The dashboard lifecycle

### Updating

`ddog` can update multiple dashboards in one go. We recommend you narrow this down to just the dashboard definitions you've changed locally and that you want to push.

```bash
(monitoring-project) $ ddog dash update-live --title '*skel*'
Updating dashboard 'xyz-123-def' entitled 'libddog skel: AWS ELB dashboard'
```

TODO: create, remove



## What Datadog features are supported?

libddog is a young project and currently supports a small but useful subset of dashboard functionality. See the **[Feature support](docs/FEATURE_SUPPORT.md)** page for details.

The skeleton project represents a minimal example of what you can do with libddog. For an exhaustive example of everything you can do with metrics and widgets have a look the definitions used in our [integration tests](../testdata).



## Keeping your code quality high

There are some helpful scripts in the `ci/` directory to run `black` (code formatter) and `mypy` (static type checker) on your project. To get these working first install the development tools:

```bash
(monitoring-project) $ pip install -r dev-requirements.txt 
```

libddog uses type annotations and we highly recommend that you take advantage of them to keep your code working correctly by running `mypy`. A clean slate execution will look like this:

```bash
(monitoring-project) $ ci/typecheck 
Success: no issues found in 5 source files
```

If you pass the wrong type of parameter to a function `mypy` will help you fix it:

```bash
(monitoring-project) $ ci/typecheck 
dashboards/aws_ec2.py:31: error: Argument "display_type" to "Request" has incompatible type "LineWidth"; expected "DisplayType"
Found 1 error in 1 file (checked 5 source files)
```