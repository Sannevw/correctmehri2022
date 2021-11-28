# Code for "Using Non-Expert Feedback to Correct Failures of Reinforcement Learning Policies After Deployment"

A modified version of the code from ["Too many cooks: Bayesian inference for coordinating multi-agent collaboration"](https://arxiv.org/pdf/2003.11778.pdf).

Original code see: [original repository](https://github.com/rosewang2008/gym-cooking)

Please use this bibtex if you want to cite this repository in your publications:
```
@article{addRef,
  title={addTitle},
  author={addAuthor},
  year={addYear}
}
```

And please use this bibtext if you want to cite the original repository in your publications:
```
@article{wang2020too,
  title={Too many cooks: Coordinating multi-agent collaboration through inverse planning},
  author={Wang, Rose E and Wu, Sarah A and Evans, James A and Tenenbaum, Joshua B and Parkes, David C and Kleiman-Weiner, Max},
  journal={arXiv preprint arXiv:2003.11778},
  year={2020}
}
```
Contents:
- [Installation](#installation)
- [Usage](#usage)
- [Environments and Recipes](docs/environments.md)
- [Design and Customization](docs/design.md)
- [Experiments from the paper](docs/replicate.md)

## Installation

You can install the dependencies with `pip3`:
```
git clone REMOVED FOR ANONYMOUS SUBMISSION
cd gym-cooking
pip3 install -e .
```

All experiments have been run with `python3`.

## Usage 

Here, we discuss how to run a single experiment, run our code in manual mode, and re-produce results in our paper. For information on customizing environments, observation/action spaces, and other details, please refer to the section on [Design and Customization](docs/design.md)

For the code below, make sure that you are in **gym-cooking/**. This means, you should be able to see the file `main.py` in your current directory.

<p align="center">
    <img src="images/5ijehz.gif" height=200 width=230></img>
</p>

### Running an experiment 

The basic structure of our commands is the following:

`python main.py --level <level name>`

where`level name` are the names of levels available under the directory `cooking/utils/levels`, omitting the `.txt`.

For example, running the salad recipe (Example 1 in the paper) looks like:
`python main.py --level tomato_salad`


### Additional commands

* `--record` will save the observation at each time step as an image in `misc/game/record`.

### Manual control

To manually control agents and explore the environment, append the `--play` flag to the above commands. Specifying the model names isn't necessary but the level and the number of agents is still required. For instance, to manually control 2 agents with the salad task on the open divider, run:

`python main.py --level tomato_salad --play`

This will open up the environment in Pygame. You can move left and right (arrow keys), press 'c' for chopping, 'f' for fetching and 'd' for delivering. Hit the Enter key to save a timestamped image of the current screen to `misc/game/screenshots`.


