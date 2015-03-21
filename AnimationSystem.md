# Introduction #

_This document is being updated, the whole engine will change to the MVC paradigm and the mediator pattern, see http://sjbrown.ezide.com/games/writing-games.html_

We face the problem of animating a 2D character in a complex space, trying to provide a smooth animation.

The main weakness of our engine is that all images must be rendered in advance.
The main advantage is that we have a 3d model to prerender all needed images we need.

# Requirements #

  * The animation must be induced by a controller (the keyboard, mouse or just a script)
  * The animation must be synchronized with the physics engine. That means it must respect collisions. To accomplish this, the animation system will message the physics engine with requests, instead of letting the controller and the physics engine communicate directly.
  * The animation must be smooth. Transitions between animation cycles must be seamless.

# Solution #

Under the new event-driven system, the animator hears to "movement petitions" that correspond to character movements. It saves the petition and waits until the cycle is ready to change,  once it is ready it sends a message acknowledging that the movement can take place and starts directing the physics engine using messages.

Character motion is directed by the animator system. This means the animator system takes the "High level" orders and directs the physic engine to generate the movement using "Low level" instructions.

# Events #

The system will send messages once any of the following happens:

  * ANIM\_CHANGE\_OK: A previously requested cycle is ready to play and will start once the physics engine acknowledges (see PhysicMachine )
  * ANIM\_CHANGE\_CANCELED: A previously requested cycle was canceled by the animation system. A possible reason is that the requested transition is impossible as a single operation.
  * ANIM\_CHANGE\_PROCESSING: A previously requested cycle is being prepared and will start once some internal process is finished (i.e. after the current cycle is finished or after a transition animation finishes playing)

The system will hear for the following messages:

  * Motion requests
  * PHYS\_CHANGE\_OK

**Example**
  1. Message received "Walk to the right"
  1. Current cycle is "Walk to the left", store "Walk to the right".
  1. It waits for confirmation from the physics engine.
  1. Once the cycle is in the right frame it sends a message acknowledging it is ok to start
  1. Cycle changes and starts.

This is a simplified version, more complex scenarios include:
  * Animator system plays an intermediate animation before acknowledging that it is ok to do the asked one (for example, turns right before starting walking)
  * Animator system sends an acknowledge before having a confirmation from the physics engine (for example, spreads wings and moves as flying even if it is not flying).