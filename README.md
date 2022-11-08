# paws-tools
collection of tools for working with PAWS


# Installation
For the python tools, prefer a python=3.9 environment.

You can create a new conda environment:
```
conda create -n paws-tools python=3.9
conda activate paws-tools
```

For production usage:
```
pip install git+https://github.com/tischfieldlab/paws-tools.git   # if you like to use git over https
pip install git+ssh://git@github.com/tischfieldlab/paws-tools.git # if you like to use git over ssh
```

For development usage:
```
git clone https://github.com/tischfieldlab/paws-tools.git
pip install -e paws-tools[dev]
```
Last part about `[dev]` is important to install required development dependencies.

