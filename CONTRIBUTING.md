# Contributing guide

## Commit guidelines

### Subject line content

The subject line of a commit should explain what files or topic in the project
is being modified as well as the overall change that is being made.

For example, if the overall documentation format is being changed to meet a new
standard, a good subject line would be as follows:

```
documentation: rework to fit standard X
```

Another example, if a specific documentation file is being changed to fix
spelling errors, a good subject line would be as follows:

```
documentation/some-file.md: fix spelling errors
```

### Subject line format

The subject line should be no longer than 72 characters. Past this it will wrap
when reading via a standard sized terminal. If the changes cannot be summarized
in that length then the commit is likely better split into multiple commits.

The `topic: summary of what changed` format is preferred but will not be
enforced. As long as it includes the topic and a summary of what changed it is
acceptible.

### Body content

The body of the commit should explain the why the commit is needed or wanted.

The body may also give more detail on what is being changed or how it is being
changed.

With simple and obvious commits this is not always necessary and the body of the
commit may be omitted.

### Body format

Body text should usually not go past 72 chacters per line. This is not a hard
rule and can be broken where appropriate. For example, if error text is included
in the commit body and is longer than 72 characters, it does not need to be
broken into shorter lines.
