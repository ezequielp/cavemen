**Emisor:** The [Physics engine](PhysicMachine.md)

**Receptor:** The map object.

# Example sequence #

  1. An object's velocity is faster than 1000 pixels per second. The physics engine posts an event saying so.
  1. The map object listens to that event and examines the object position. The object is outside the map's limits.
  1. The map object kills the object.