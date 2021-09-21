# Changelog

## 0.0.7 (next)

...

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
