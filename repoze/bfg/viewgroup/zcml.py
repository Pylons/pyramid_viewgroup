from zope.interface import Interface

from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import Tokens

from zope.schema import TextLine

from repoze.bfg.interfaces import IView

from repoze.bfg.configuration import Configurator
from repoze.bfg.viewgroup.group import ViewGroup
from repoze.bfg.threadlocal import get_current_registry

"""
<bfg:viewgroup
  name="headers"
  viewnames="header1 header2 header3"
  for=".interfaces.IContent"
/>
"""

def viewgroup(_context,
              name="",
              viewnames=None,
              for_=None,
              ):

    if not viewnames:
        raise ConfigurationError('"viewnames" attribute was not specified')

    viewgroup = ViewGroup(name, viewnames)
    reg = get_current_registry()

    def register():
        config = Configurator(reg, package=_context.package)
        config.add_view(viewgroup, name=name, context=for_, _info=_context.info)

    discriminator = ('view', for_, name, None, IView, None,
                     None, None, None, None, None, None, None, None)
    

    _context.action(
        discriminator = discriminator,
        callable = register,
        )

class IViewGroupDirective(Interface):
    name = TextLine(
        title=u"The name of the viewgroup",
        description=u"",
        required=False,
        )

    for_ = GlobalObject(
        title=u"The context interface this viewgroup is for.",
        required=False
        )

    viewnames = Tokens(
        title=u"",
        description=(u"The viewnames used to provide the content (in "
                     u"the order which they will be rendered)"),
        required=False,
        value_type=TextLine(),
        )

