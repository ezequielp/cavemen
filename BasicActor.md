# `Basic_Actor` #
_Extends `pygame.sprite.Sprite`_

This class will implement the basic requirements to any entity moving in the game's world. It inherits from pygame's Sprite class and has a [`state\_machine` class](StateMachineClass.md) to implement AI.

## Features needed ##

  * Owns a finite state machine using the [state machine class](StateMachineClass.md).
  * Implements a physics engine that allows moving the entity in the map by use of the following interface:
    * `set_steering_force()`: sets a force applied to the actor
    * `turn_gravity_ON()`: Adds a gravitational force to the movement
    * `turn_gravity_OFF()`: Removes the gravitational force. (for example, when standing on floor)
  * Implements the update of the actor's coordinates using the standard Update method, as expected by the parent class Sprite

## Parents ##

[`pygame.sprite.Sprite`](http://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite)

## Children ##

[caveman](Caveman.md)