
## Introduction

`flowws` is an in-development framework for building modular, reusable
task workflows. The core library contains tools to abstract over
storage locations and parse arguments in a uniform way for both python
scripts and command-line-based execution.

`flowws` is being developed in conjunction with other projects, including:

- [hoomd-flowws](https://github.com/klarh/hoomd_flowws): perform simulations with [hoomd-blue](https://github.com/glotzerlab/hoomd-blue).
- [flowws-analysis](https://github.com/klarh/flowws-analysis): run analysis and visualization workflows
- [flowws-freud](https://github.com/klarh/flowws-freud): molecular simulation-specific modules for `flowws-analysis`

## Installation

Install flowws from PyPI:

```
pip install flowws
```

Alternatively, install from source:

```
pip install git+https://github.com/klarh/flowws.git#egg=flowws
```

## Documentation

Browse more detailed documentation
[online](https://flowws.readthedocs.io) or build the sphinx
documentation from source:

```
git clone https://github.com/klarh/flowws
cd flowws/doc
make html
```
