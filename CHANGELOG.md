# Changelog

## 0.1.0

- Deprecated the `title` parameter to `Request` as a way to set a label for a
  query. From now on the `title` parameter can still be set, but is a noop. It
  will eventually be removed. Passing `title` also raises a `DeprecationWarning`
  which is printed to stderr. Issue #50.
- Added a cookbook with an entry that explains how to set the label for a query
  using a `Formula`.

## 0.0.8

- Added validation to make sure that all query names in a `Request` are unique.
  The validation runs when the `Request` is constructed. Formula validation now
  also runs at `Request` construction time, to avoid a latent error. Issue #45.

## 0.0.7

- Added an upgrade-check in the cli. When using the cli it checks the installed
  version against the latest version in PyPI and gives instructions on how to
  upgrade. The check is not repeated for the next 24h. The flag
  `--no-upgrade-check` tells the cli to skip the check.

## 0.0.6

- In `ddog dash list-defs` removed the `ID` column because dashboard
  definitions do not need to have a populated id.
- The dashboard description footer now also includes the version of libddog that
  was used in the update.

## 0.0.5

- Fixed bug in `ddog dash publish-draft` and `publish-live` failing on a
  `Dashboard` object with a populated `.id` attribute. Issue #35.

## 0.0.4

- Added metadata blurb (footer) to dashboard descriptions to show that:
    - The dashboard is maintained using libddog.
    - Changes to the dashboard made manually could be lost.
    - A link to the project repo, if available (detected via the git remote).
    - When the dashboard was last updated.
    - Which branch the dashboard was last updated from, if available.

## 0.0.3

- New commands introduced for `ddog dash`:
    - `delete-live` to delete a dashboard in Datadog.
    - `list-live` to list dashboards in Datadog.
    - `publish-draft` to publish a definition as a draft dashboard in Datadog.
    - `publish-live` to publish multiple definitions as dashboards in Datadog.
    - `snapshot-live` to create an on disk snapshot of a dashbord in Datadog.
- Commands removed from `ddog dash`:
    - `update-live` removed in favor of `publish-live`.

## 0.0.2

- Added docs.
- Added docs/skel - an example skeleton project.
- Added `ddog version` command.

## 0.0.1

First public release.
