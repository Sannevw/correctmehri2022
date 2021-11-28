# Experiment Replication Details

This page contains the implementation and experiment details for 

[Experiment 1: Alternative Action :tomato: ](#alternative-action)

[Experiment 2: Alternative Ingredient :cake:](#alternative-ingredient)

[Experiment 3: Shielded Action :safety_vest:](#shielded-action)


## Alternative Action 

### Training an :blue_square: initial agent, to perform the task: delivering a tomato salad recipe.

The recipe consists of 1 ChoppedTomato + 1 ChoppedLettuce + 1 Plate

<figure>
<img src="../images/ex1_numbered.png" width="200" height="200"> 
  <figcaption>Fig.1 - The tomato salad environment. </figcaption>
</figure>

To train the agent, run the following command:

`python main.py --level tomato_salad --max_num_timesteps 50 --num_episodes 500 --lr 0.6 --gamma 0.8`


### Run the trained  :blue_square:	initial agent

To run the trained :blue_square: initial agent, run the following command:

`python run_trained.py --level tomato_salad --record --fname {file_name.pkl}`

The trained agent should correctly deliver the tomato salad, using the readily available chopped tomato ([5] in Fig 1.):

<figure>
<img src="../images/ex1_initialAgent.gif" width="200" height="200"> 
  <figcaption>Fig.2 - The agent successfully learned to make a tomato salad. </figcaption>
</figure>


The pickle files for the salad and coffee can be found in misc/metrics/pickles/salad/ and misc/metrics/pickles/coffee, the cake pickle files are not added to this submission due to large file size.

### Re-training when there is no chopped tomato readily available

Someone takes the last tomato slice or there are no sliced tomatos available in this new kitchen environment the robot is deployed in. This means that the start state is unseen: it starts in a kitchen in which the tomato slice is not available, hence, the state encoding will be different.

#### Without shielding

`python main.py --level tomato_salad_placeholder --pretrained --fname init_agent.pkl --num_episodes 250 --max_num_timestep 50 --epsilon 0.1 --num_runs 10 --lr 0.6 --gamma 0.8`


#### With shielding 

Add the `--shield` flag.

`python main.py --level tomato_salad_placeholder --pretrained --fname init_agent.pkl --num_episodes 250 --max_num_timestep 50 --epsilon 0.1 --num_runs 10 --lr 0.6 --gamma 0.8 --shield`

## Alternative Item 

### Training an :red_square: initial agent, to perform the task: baking a cake.

The recipe consists of 1 Eggs + 1 Flour + 1 Bowl --> Bake Bowl with eggs and flour.

<figure>
<img src="../images/ex2_numbered.png" width="200" height="200"> 
  <figcaption>Fig.4 - The cake baking environment. </figcaption>
</figure>

`` 


### Run the trained :red_square:	initial agent

To run the trained :red_square: initial agent, run the following command:

`python run_trained.py --level flour_alternative --record --fname {file_name.pkl}`

This should work and deliver a cake, using the regular flour (Fig 2.):

<figure>
<img src="../images/ex2_initialAgent.gif" width="200" height="200"> 
  <figcaption>Fig.2 - The agent successfully learned to bake a cake. </figcaption>
</figure>

In this case, the agent was successful in 394 of 500 episodes, 0.788 percent of the time.

### Re-training when there is no regular flour readily available

Similar to the previous example, we replace the Regular Flour with a 'placeholder'. This is an invisible object, which is an implementation choice, to keep the same number of objects which determines the state space size in our implementation. 

#### Without shielding

`python main.py --level flour_alternative_placeholder --pretrained --fname init_agent.pkl --num_episodes 250 --max_num_timestep 50 --epsilon 0.1 --num_runs 10 --lr 0.6 --gamma 0.8` 


#### With shielding 

Add the `--shield` flag.

`python main.py --level flour_alternative_placeholder --pretrained --fname init_agent.pkl --num_episodes 250 --max_num_timestep 50 --epsilon 0.1 --num_runs 10 --lr 0.6 --gamma 0.8` 


## Forbidden Action 

### Training an 🟩 initial agent, to perform the task: deliver a coffee. 

The task consists of fetching the coffee and delivering it at the *.

`python main.py --level coffee_simple --num_episodes 200 --max_num_timesteps 150`

### Run the trained  :blue_square:	initial agent

To run the trained 🟩 initial agent, run the following command:

`python run_trained.py --level coffee_simple --record --fname {file_name.pkl}`

This shows the agent correctly delivering the coffee at the Delivery tile.


<figure>
<img src="../images/ex3_coffee_initialAgent.gif" width="200" height="200"> 
  <figcaption>Fig.6 - The agent successfully learned to deliver coffee. </figcaption>
</figure>


### Re-training when there is carpet in the kitchen. 

Now, the robot is placed in someone's kitchen and the environment's layout changed. There is carpet in some places, where there was linoleum floor before. The robot cannot drive over the carpet tiles, it gets stuck on the carpet.

#### Without shielding

`python main.py --level coffee_simple_carpet --pretrained --fname init_agent.pkl --num_episodes 250 --max_num_timestep 50 --epsilon 0.1 --num_runs 10 --lr 0.6 --gamma 0.8` 


#### With shielding 

Add the `--shield` flag.

`python main.py --level coffee_simple_carpet --pretrained --fname init_agent.pkl --num_episodes 250 --max_num_timestep 50 --epsilon 0.1 --num_runs 10 --lr 0.6 --gamma 0.8 --shield` 


