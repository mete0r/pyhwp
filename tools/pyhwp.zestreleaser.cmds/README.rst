pyhwp.zestreleaser.cmds
=======================

A zest.releaser plugin to provide command hooks

For each [prerelease, release, postrelease] x [before, middle, after] hooks,
run executable files in ``release-hooks/{A}.{B}/`` (in alphabetical order).
