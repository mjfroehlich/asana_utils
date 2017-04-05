# asana_utils

Helpers for making Asana even nicer.

[![Build Status](https://travis-ci.org/mjfroehlich/asana_utils.svg?branch=master)](https://travis-ci.org/mjfroehlich/asana_utils)

## Usage

All scripts expect a valid personal Asana access token in the `ASANA_ACCESS_TOKEN`
environment variable.

### asana_meta_from_name

Set task metadata (project membership, tags, status) via special strings in
task name.

Example: Task `foo t:bar p:baz p:qux` is turned into task `foo`, which is part
of projects `baz` and `qux`, plus is tagged `bar`.

Specified tags/projects which don't exist are created.

Supported commands:
```
  t:<string>                                        # Add tag to task
  p:<string>                                        # Add task to project
  s:<"inbox" | "later" | "today" | "upcoming">      # Update assignee status
```

Motivation: I love creating Asana tasks through browser plugins or per mail,
because I'm not exposed to a (distracting) whole list of tasks once I open
asana.com.
The only downside are the limited task-editing capabilities, which force upon
the user the additional task of organising new tasks in batch, which can be
quite a nuisance when using Asana extensively...

`<some blog post I need to read at some point> t:2read s:later` is just so
helpful in not congesting the new tasks bucket.


## Installing

`python setup.py install` creates console scripts

## Testing

`python setup.py test`, `pip install tox; tox`
