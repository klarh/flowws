
## Introduction

`flowws` is an in-development framework for building modular, reusable
task workflows. The core library contains tools to abstract over
storage locations and parse arguments in a uniform way for both python
scripts and command-line-based execution.

`flowws` is being developed in conjunction with
[hoomd-flowws](https://github.com/klarh/hoomd-flowws), which
implements a set of flowws modules for use with
[hoomd-blue](https://github.com/glotzerlab/hoomd-blue).

## Installation

Install flowws from source using `pip`:

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
