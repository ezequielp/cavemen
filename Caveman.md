# Caveman #

The caveman is one of the game entities. It moves on the different floors of the level.

![http://cavemen.googlecode.com/svn/trunk/media/CavemanAnim.png](http://cavemen.googlecode.com/svn/trunk/media/CavemanAnim.png)
> _Image used for testing purposes_

The caveman will be the main entity of the game, reacting to the player's actions but not being directly commanded by him.

# Features Needed #

  * It stores the floor it is standing on and moves over it with a 1D coordinate
  * All the caveman movements are constrained on the floor
  * It starts in a [wandering state](StateWandering.md) and diffuses [through doors](StateUsingDoor.md).

## Parent ##

[`Basic\_Actor`](BasicActor.md)