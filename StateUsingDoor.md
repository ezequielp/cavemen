# `State_Using_Door` #

This is an intermediate state used when entering a door. The basic behavior is switching to a new [wandering state](StateWandering.md) determined by the door's destination, but more complex behavior can be programmed.

This state could be created using a factory method in the door class.

## Possible improvement ##

  * Cave Doors where the caveman can be safe
  * Time to travel through the door

## Enter behavior ##

Maybe an animation where the door is opened if not already and the caveman enters

## Execute behavior ##

The agent is put in a "inside door" state. Then it changes to a wandering state outside the other door.

## Exit behavior ##

Maybe an animation where the door is opened if not already and the caveman exits