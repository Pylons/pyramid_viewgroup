pyramid_viewgroup
====================

``pyramid_viewgroup`` is an extension for the ``pyramid`` web framework. The
extensio makes it possible to make a ``viewgroup`` declaration which acts
much like ``view`` inasmuch as it results in a Pyramid view registration.
Unlike a "normal" ``view`` registration, however, a ``viewgroup``
registration refers to one or more other Pyramid views (matching them by
name, ``for`` interface, and request type).  When a ``viewgroup`` is invoked
(either via traversal or via programmatic view execution), a viewgroup will
return a response which appends all the referenced view renderings together
in a single body.

For more information see http://docs.pylonshq.com/pyramid_viewgroup/dev/

