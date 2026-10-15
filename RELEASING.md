# Releasing

1. Bump the version in `pyproject.toml` and `src/ternwire/__init__.py` and merge it to `main`.
2. Tag that commit and push the tag:

   ```sh
   git tag v0.1.1 && git push origin v0.1.1
   ```

3. The Publish workflow checks that the tag matches the version, runs the checks, and
   waits for a maintainer to approve the `release` environment. Approve it in the
   workflow run.

Published versions are immutable, and the repository blocks moving or deleting `v*`
tags. To fix a bad release, publish a new version.

## One-time setup

Publishing uses PyPI trusted publishing, so no token is stored. On PyPI, add a
GitHub publisher to the `ternwire` project with owner `ternwire`, repository
`ternwire-python`, workflow `publish.yml`, and environment `release`. Before the first
release, add it as a pending publisher under Account, Publishing instead.
