# `Base_State` #

This class gives the interface of a simple state. The state itself doesn't do anything, and does not provide any switch logics, so it shouldn't be used except as a parent class of actual states.

Transitions can be deterministic using access to the agent's internal variables and the world's variables but it can also be probabilistic (see basic Wandering state)

All state logic will be contained inside the state.

## Methods ##

  * `__init__(owner)`:
  * `enter()`: Runs when first started
  * `execute()`: Runs on each step
  * `exit()`: Runs when exited

## Children ##

[State\_Wandering](StateWandering.md)