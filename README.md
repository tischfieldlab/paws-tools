# paws-tools
[![CI](https://github.com/tischfieldlab/paws-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/tischfieldlab/paws-tools/actions/workflows/ci.yml)

A collection of tools for working with PAWS


# Installation
For production usage:
```
pip install git+https://github.com/tischfieldlab/paws-tools.git   # if you like to use git over https
pip install git+ssh://git@github.com/tischfieldlab/paws-tools.git # if you like to use git over ssh
```

For development usage, use one of the following:
```
git clone https://github.com/tischfieldlab/paws-tools.git
cd paws-tools
conda env create -f environment.yml
```
```
git clone https://github.com/tischfieldlab/paws-tools.git
cd paws-tools
pip install -e .[dev]
```
Last part about `[dev]` is important to install required development dependencies.
See [`CONTRIBUTING.md`](CONTRIBUTING.md) for more information on development.


## Usage
Please check out the command line interface:
```
$ paws-tools --help
Usage: paws-tools [OPTIONS] COMMAND [ARGS]...

  Toolbox for working with PAWS.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  slp-to-paws-csv  convert SLEAP .slp file to PAWS importable csv files
```

## Support
For technical inquiries specific to this package, please [open an Issue](https://github.com/tischfieldlab/paws-tools/issues)
with a description of your problem or request.

Other questions? Reach out to `thackray@rutgers.edu`.

## License
This package is distributed under a BSD 3-Clause License and can be used without
restrictions. See [`LICENSE`](LICENSE) for details.
