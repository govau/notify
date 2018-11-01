# Notify docs

Notify docs are a set of static assets built through Gatsby.

## First-time setup

You'll need Node and NPM.

```shell
brew install node
```

Install dependencies and build the docs

```shell
make install
make build
```

## Developing with hot reload

Running this command in a shell will run up a Gatsby server that reloads
whenever source files change. It should be used while you develop the docs.

```
make run
```

## Where things belong

We make heavy use of MDX for our pages and code examples. MDX files placed in
`src/content` will be picked up and turned into pages automatically by Gatsby.

Code samples should be written in MDX, and be placed in `src/code-examples` in
an appropriate directory. When we load an `Example` component, it will search
for the correct sub-directory and all of the MDX files it contains.

React components that are re-used across pages, markdown, and code examples,
should all go in `src/components`.
