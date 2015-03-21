# `State_Wandering` #

This state makes a walking actor(like a caveman) travel through the map using a basic diffusive behavior. The caveman will move from one cliff to the other of its current floor and will decide to travel to a safer ground in a non deterministic way.

### Possible improvements ###

  * Make movement more "human like", i.e. Make the actor stop to rest, add noise to trajectory (see [Perlin noise](http://freespace.virgin.net/hugo.elias/models/m_perlin.htm)).

## Enter behavior ##

When entering to a new floor, it will change the agent's position to the corresponding door and load the left, right cliff positions and the doors.

## Execute behavior ##

Execute will decide one of the following objectives and walk there using a [seek steering](SteeringBehaviorSeek.md):
  1. left cliff
  1. right cliff
  1. door

It will change to the [entering door state](StateEnteringDoor.md) when arrived at an objective door.
It will change direction and objective when arrived at a cliff.




## Parents ##