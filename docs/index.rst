pyramid_viewgroup
====================

``pyramid_viewgroup`` is an extension for the ``pyramid`` web framework. The
extensio makes it possible to make a configurator method call to
``add_viewgroup`` which acts much like ``add_view`` inasmuch as it results in
a Pyramid view registration.  Unlike a "normal" ``add_view`` registration,
however, an ``add_viewgroup`` registration refers to one or more other
Pyramid views (matching them by name, ``context`` interface, and request
type).  When a ``viewgroup`` is invoked (either via traversal or via
programmatic view execution), a viewgroup will return a response which
appends all the referenced view renderings together in a single body.

This package is largely by request for folks that enjoy using Zope 3 "content
providers" and "viewlets", although it is slightly less featureful, as
Pyramid views themselves typically do not possess an interface (they're just
callables), so you cannot register a viewgroup against a view interface.

Note that the author of ``pyramid_viewgroup`` disagrees with the concept on
which its based; it seems more straightforward and understandable to him to
just do the work in a view itself without all this stupid machinery (the docs
for this are particularly painful to write because they're entirely
self-referential, a sure sign of stupid machinery, so forgive me if I have
trouble explaining it).  This is largely just a proof of concept, although a
tested and functional one.

Installation
------------

Install using setuptools, e.g. (within a virtualenv)::

  $ easy_install pyramid_viewgroup

Usage
-----

To use a viewgroup, you must:

#. Use ``config.include('pyramid_viewgroup')``.

#. Subsequently call ``config.add_viewgroup(name, viewnames)`` or create a
   ZCML registration which registers a viewgroup.

#. Either invoke the viewgroup via normal URL traversal like a regular
   view - OR - use the ``provider`` API to inject content into your
   template using the viewgroup name.

Imperative Usage
++++++++++++++++

.. code-block:: python
   :linenos:

   # config is a Configurator instance

   config.include('pyramid_viewgroup')
   config.add_viewgroup('tabs_group', viewnames=('login_tab', 'content_tab'), 
                        context='myproject.interfaces.ISite')

The consituent attributes of the ``add_viewgroup`` configurator method are:

``name`` -- The name by which the viewgroup can be found via traversal
  or programmatic view execution.  This argument has the same meaning
  as the ``name`` argument in a ``view`` directive.

``viewnames`` -- The view names (in render order) which will be
  rendered when this viewgroup is rendered, separated by spaces.  Each
  name should refer to a view name defined elsewhere in ZCML.

``context`` -- The "resource" interface which this view is registered for
  This argument has the same meaning as its counterpart in ``view``
  directive.

The ``context`` argument is optional; it defaults to ``None``.  The ``name``
argument is also optional.  It defaults to the empty string (indicating the
default view).

Viewgroups registered wih a ``name`` and a ``context`` and will conflict with
views registered with the same arguments, so it's wise to name your
viewgroups differently than your views.

A viewgroup can refer to another viewgroup in its ``viewname`` argument as
necessary (although this is insane).

ZCML Usage
++++++++++

You can use ZCML instead of imperative configuration.  First include the
meta.zcml for pyramid_viewgroup:

.. code-block: xml
   :linenos:

   <include package="pyramid_viewgroup" file="meta.zcml"/>

Then create a ``viewgroup`` registration in ZCML via the ``viewgroup``
directive::

  <viewgroup
    name="tabs_group"
    viewnames="login_tab content_tab"
    context=".interfaces.ISite"
   />

The consituent attributes of this directive are:

``name`` -- The name by which the viewgroup can be found via traversal
  or programmatic view execution.  This attribute has the same meaning
  as the ``name`` attribute in a ``view`` directive.

``viewnames`` -- The view names (in render order) which will be
  rendered when this viewgroup is rendered, separated by spaces.  Each
  name should refer to a view name defined elsewhere in ZCML.

``context`` -- The "model" interface which this view is registered for This
  attribute has the same meaning as its counterpart in ``view`` directive.
  For backwards compatibility, in ZCML, this attribute can also be referred
  to as ``for_``.

What Happens When a Viewgroup is Rendered
+++++++++++++++++++++++++++++++++++++++++

When a viewgroup is rendered, it attempts to render each constituent
view it references (via ``viewnames``).  If an individual constituent
view cannot be rendered due to a permission issue, it is skipped over.
If a constituent view cannot be rendered because it cannot be found, a
``ValueError`` is raised.  The rendering of a viewgroup is the simple
concatenation of all allowed views referenced by the viewgroup.

Provider Helper
+++++++++++++++

A helper class named ``pyramid_viewgroup.Provider`` is made
available for those wishing to render viewgroups within templates.  An
instance of ``Provider`` can be constructed and passed into a template
rendering so it may be used ala the ``provider:`` expression type in
Zope 3.  For example, this view might render a template::

  from pyramid.view import view_config
  from pyramid_viewgroup import Provider

  @view_config(renderer='templates/mytemplate.pt')
  def myview(context, request):
      provider = Provider(context, request)
      return {'provider':provider}

The template being rendered can use the provider to "fill slots" by
passing in view or viewgroup names as necessary, e.g.::

  <html>
    <head>
     <span tal:replace="structure provider('headgroup')/>
    </head>
    <body>Hello!</body>
  </html>

The names passed in to a provider should be either a view name or a viewgroup
name.

Reporting Bugs / Development Versions
-------------------------------------

Visit https://github.com/Pylons/pyramid_viewgroup/issues to report bugs.
Visit https://github.com/Pylons/pyramid_viewgroup to download development or
tagged versions.

Indices and tables
------------------

* :ref:`modindex`
* :ref:`search`
