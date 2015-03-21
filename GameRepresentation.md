# Introduction #

Here we present a few ideas about the abstract representation of some of the features of the game.

# Behaviors and Graphs #
The state of and actor in the game can be represented as a two element vector.


&lt;math&gt;

S=\left(behavior, variables\right)

&lt;/math&gt;


The first element, _behavior_, is a flag that indicates the behavioral state of the actor (wandering, fleeing, pursuing,...). each of this behaviors has dependencies on internal variables that changes the way the behavior is represented in the agent, for example, the wandering the speed of the wandering state could depend on the value of a variable "fatigue". But if the actor has drained all its energy (that means fatigue is at its maximum value) then the behavior should switch to "sleep" or an equivalent. A way of expressing this could be

> 

&lt;math&gt;

S=\left(wandering(fatigue), exhausted\right)

&lt;/math&gt;



The variable exhausted takes values 0 or 1. Usually the "external" variables (variable exhausted in the example) are derived not only from internal states but from interactions with the environment, for example variables like "fear", "hunger", "anger". The idea is that this variables will be highly correlated with the actions of the player, in such a way that the actions performed by the player can induce changes in the behaviors of the actors.

As one can forecast, the dimension of the State can be huge. So we are interested in some projections. There are two projections that call our attention:
# State-behavior -> SB=(behavior)
# State-varible -> SV=(variables)

If we have many possible behaviors there should be a transition matrix between them. That is a matrix expressing how these behaviors are connected and the weights of these connections. The weights, for instance, could be represented by the probability of going from behavior A to behavior B given the set of variables.

> 

&lt;math&gt;

 W<sub>BA</sub>=H(A,B | SV)

&lt;/math&gt;



With this representation we can study the evolution of the game as the number of actors in a particular point on SB. This can be thought as a graph with nodes given by SB elements and connections given by W<sub>BA</sub>.
One simple way of designing objectives for a level would be to specify the population of each node and the maximal fluctuations of this population.
An example of this way of designing levels would be one where the player is expected to produce an exodus of the actors. That would mean that through interactions the player should drive most of the population to be in a "fleeing" behavior or a compound behavior "migrating". As anyone can realize there could be more than one way to achieve this (winning strategies diversity) like destroying all the resources systematically or rising fear among the population.