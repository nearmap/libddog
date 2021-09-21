# User guide



## How to get started

libddog requires **Python 3.8** or later.

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

You can now use the `ddog` command line tool to manage your dashboards. To verify that it's working correctly:

```bash
(monitoring-project) $ ddog version
libddog version 0.0.6
```

Next time you return to the project you will just need to activate the virtual environment before you start working on it:

```bash
$ workon monitoring-project
(monitoring-project) $
```

> `libddog` is an actively developed project with [improvements](../CHANGELOG.md) being made frequently. We highly recommend staying close to the [latest version](https://pypi.org/project/libddog/#history). You can update libddog by doing `pip install -U libddog` in your virtual environment.



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

Dashboards generally follow a lifecycle that goes approximately like this...

You perceive the need for a new dashboard. You go into the Datadog UI and experiment with different metrics and widgets, coming up with a useful proof of concept. At this point, what you decide to do next will depend on your use case. Some dashboards are short lived and only used for a one-off load test or investigation. Other dashboards become part of your team's dashboard collection that you want to maintain long term.

Once you've decided that you want to define this dashboard in code you start creating a dashboard definition for it using the libddog API. This does not happen all at once - it's an incremental process. You want to try things out in code, see how it looks and works in Datadog, make further changes, refactor something etc. It works much like any software development effort. During this time it's super useful to be able to see and test each iteration you create in Datadog. But this is not the final dashboard yet, it's a draft dashboard.

Once you're happy with the draft you want to publish the final dashboard. It's now ready for other people to use as well, and you should strive to keep it in good working condition from now on. Think of it as production software.

From time to time you'll need to make updates to your dashboard. Minor updates can be done in place (like pushing to *master*). Major updates introduce the risk of breaking the working dashboard, so it's better to do them on a draft (like using a feature branch). Once you're happy with the state of the draft, you push those changes to the production dashboard again.

One day, the dashboard is no longer needed and it's time to delete it. At this point you may want to take one last snapshot of it in case you change your mind and want to restore it.


### Listing your dashboard definitions

`ddog dash list-defs` gives you a listing of all your dashboard definitions.

```bash
(monitoring-project) $ ddog dash list-defs
GROUPS  WIDGETS  QUERIES  TITLE
     0        1        1  libddog skel: AWS ELB dashboard
```


### Listing dashboards in Datadog

`ddog dash list-live` gives you a listing of the dashboards that exist in your organization's account in Datadog, whether they have a corresponding definition in code or not.

```bash
(monitoring-project) $ ddog dash list-live
         ID                AUTHOR    CREATED   MODIFIED  TITLE
rmz-br5-j7h       martin.matusiak    18 days    44 mins  libddog QA: exercise metrics queries
km5-y3y-4vq       martin.matusiak    1 hours    44 mins  libddog QA: exercise widgets
```


### Working on a draft

When you're developing a new dashboard or redesigning an existing dashboard it's best to do this as a draft. You will use `ddog dash publish-draft` to publish the draft. The string `[draft] ` will be prepended to the title of the dashboard to mark it as a draft.

The first time you publish a dashboard as a draft it does not exist yet so it's created:

```bash
(monitoring-project) $ ddog dash publish-draft -t '*skel*'
Creating dashboard entitled: '[draft] libddog skel: AWS ELB dashboard'... created with id: '7rf-b25-jht'
```

It will then show up in your listing of dashboards:

```bash
(monitoring-project) $ ddog dash list-live
         ID                AUTHOR    CREATED   MODIFIED  TITLE
rmz-br5-j7h       martin.matusiak    18 days    44 mins  libddog QA: exercise metrics queries
km5-y3y-4vq       martin.matusiak    1 hours    44 mins  libddog QA: exercise widgets
7rf-b25-jht       martin.matusiak     1 mins     1 mins  [draft] libddog skel: AWS ELB dashboard
```

The next time you publish the draft it will update the draft dashboard that's already there:

```bash
(monitoring-project) $ ddog dash publish-draft -t '*skel*'
Updating dashboard with id: '7rf-b25-jht' entitled: '[draft] libddog skel: AWS ELB dashboard'... done
```

`publish-draft` operates on a single definition because you typically work on one draft at a time.


### Publishing a final dashboard

Once you are ready to publish your definition as a production dashboard you will use `ddog dash publish-live`. If the dashboard does not exist yet it will be created:

```bash
(monitoring-project) $ ddog dash publish-live -t '*skel*'
Creating dashboard entitled: 'libddog skel: AWS ELB dashboard'... created with id: 'm74-ng8-93x'
```

It will then show up in your listing of dashboards:

```bash
(monitoring-project) $ ddog dash list-live
         ID                AUTHOR    CREATED   MODIFIED  TITLE
rmz-br5-j7h       martin.matusiak    18 days    57 mins  libddog QA: exercise metrics queries
km5-y3y-4vq       martin.matusiak    1 hours    57 mins  libddog QA: exercise widgets
7rf-b25-jht       martin.matusiak     9 mins     5 mins  [draft] libddog skel: AWS ELB dashboard
m74-ng8-93x       martin.matusiak     2 mins     1 mins  libddog skel: AWS ELB dashboard
```

Notice that the draft dashboard is still there too.

Next time you publish the production dashboard again it already exists, so it will be updated. But as a precaution a snapshot is taken first:

```bash
(monitoring-project) $ ddog dash publish-live -t '*skel*'
Creating snapshot of live dashboard with id: 'm74-ng8-93x'... saved to: /home/username/src/monitoring-project/_snapshots/m74-ng8-93x--libddog_skel__AWS_ELB_dashboard--2021-08-31T00:36:52Z.json
Updating dashboard with id: 'm74-ng8-93x' entitled: 'libddog skel: AWS ELB dashboard'... done
```

`publish-live` operates on multiple definitions. When making code changes in your definitions sometimes you make changes that affect multiple dashboards, so updating them all in one go is useful.

**WARNING:** Even though snapshots are taken `publish-live` is still a destructive operation and we recommend that you only update dashboards whose definitions you have changed, and avoid using `'*'` (wildcard that matches all definitions).


### Taking a snapshot of a dashboard

Once a dashboard exists in Datadog you can take a snapshot of it any time with `ddog dash snapshot-live`. This is equivalent to the `Export dashboard JSON` option in the Datadog UI. The snapshot is stored on disk as a JSON document and can be used to manually restore the dashboard in the Datadog UI.

```bash
(monitoring-project) $ ddog dash snapshot-live -i m74-ng8-93x
Creating snapshot of live dashboard with id: 'm74-ng8-93x'... saved to: /home/username/src/monitoring-project/_snapshots/m74-ng8-93x--libddog_skel__AWS_ELB_dashboard--2021-08-31T00:42:23Z.json
```


### Deleting a dashboard

You can delete a dashboard with `ddog dash delete-live`. Before deletion a snapshot is taken in case you change your mind and want to restore the dashboard later.

```bash
(monitoring-project) $ ddog dash delete-live -i m74-ng8-93x
Creating snapshot of live dashboard with id: 'm74-ng8-93x'... saved to: /home/username/src/monitoring-project/_snapshots/m74-ng8-93x--libddog_skel__AWS_ELB_dashboard--2021-08-31T00:46:47Z.json
Deleting live dashboard with id: 'm74-ng8-93x'... done
```



## Which Datadog features are supported?

libddog is a young project and currently supports a small but useful subset of dashboard functionality. See the **[Feature support](FEATURE_SUPPORT.md)** page for details.

The skeleton project represents a minimal example of what you can do with libddog. For an exhaustive example of everything you can do with metrics and widgets have a look at the definitions used in our [integration tests](../testdata).



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
