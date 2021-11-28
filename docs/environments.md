
## Environments and Recipes

Please refer to our [Overcooked Design Document](design.md) for more information on environment/task customization and observation/action spaces.

Our environments and recipes are combined into one argument. Here are the environment

# tomato_salad

A single 3x3 kitchen space, with objects placed in a circle around the agent. The agent can move left and right to position itself towards a certain object or workspace (e.g., knife station).

To run this environment on our available recipes (tomato, tomato-lettuce, and salad), run `main.py` with the following argument:

`python main.py --level tomato_salad ...other args...`

<p align="center">
<img src="/images/open.png" width=300></img>
</p>
