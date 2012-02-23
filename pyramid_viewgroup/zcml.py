from zope.interface import Interface

from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import Tokens

from zope.schema import TextLine

from pyramid_viewgroup import add_viewgroup

from pyramid_zcml import with_context

"""
<viewgroup
  name="headers"
  viewnames="header1 header2 header3"
  context=".interfaces.IContent"
/>
"""

def viewgroup(_context,
              name="",
              viewnames=None,
              for_=None,
              context=None,
              ):

    if not viewnames:
        raise ConfigurationError('"viewnames" attribute was not specified')

    config = with_context(_context)

    if not hasattr(config, 'add_viewgroup'):
        config.add_directive('add_viewgroup', add_viewgroup)

    context = context or for_

    config.add_viewgroup(name, viewnames, context=context)

class IViewGroupDirective(Interface):
    name = TextLine(
        title=u"The name of the viewgroup",
        description=u"",
        required=False,
        )

    context = GlobalObject(
        title=u"The context interface this viewgroup is for.",
        required=False
        )

    for_ = context # bw compat

    viewnames = Tokens(
        title=u"",
        description=(u"The viewnames used to provide the content (in "
                     u"the order which they will be rendered)"),
        required=False,
        value_type=TextLine(),
        )

