# Iris's official packages

This repository holds the add-on packages that the Iris project makes. Iris is a self-hosted platform for a personal AI agent. A package is what an administrator adds to an instance of Iris: one folder whose top holds a declaration, `iris-package.json`.

The Iris project writes this repository. Each package is one folder:

| Folder | Package |
|---|---|
| [`search`](search/iris-package.json) | Search: the tools `web_search` and `web_extract`, through Firecrawl |

## How a package reaches an instance

A package here isn't offered to any instance until the project's catalogue names it. The catalogue is a list in its own repository, [iris-agent-package-catalogue](https://github.com/iris-agent-project/iris-agent-package-catalogue). Each line of the list names a folder of this repository, one commit and the package's digest.

A push to this repository publishes nothing by itself. The push reaches instances when the project moves the package's line to the pushed commit. A line moves only to a higher version.

A package is its folder at one commit, with no archive. Nothing is built, and no dependency is fetched. A file outside a package's folder, such as this page, isn't part of any package.

## Check a package

You check a package with the Iris SDK's conformance run, which proves the package against a fake of each service it reaches. With the SDK installed, run this command from the repository's top:

```sh
iris-sdk check search
```

## Licence

This repository is licensed under the [Apache License 2.0](LICENSE).
