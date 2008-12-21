from zope.interface import Interface
from zope.component.interface import provideInterface
from zope.component import getSiteManager

from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import Tokens

from zope.schema import TextLine

from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import IView

from repoze.bfg.viewgroup.group import ViewGroup

"""
<bfg:viewgroup
  name="headers"
  viewnames="header1 header2 header3"
  for=".interfaces.IContent"
  request_type="repoze.bfg.interfaces.IRequest"
/>
"""

def handler(methodName, *args, **kwargs):
    method = getattr(getSiteManager(), methodName)
    method(*args, **kwargs)

def viewgroup(_context,
              name="",
              viewnames=None,
              for_=None,
              request_type=IRequest,
              ):

    if not viewnames:
        raise ConfigurationError('"viewnames" attribute was not specified')

    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
            )

    viewgroup = ViewGroup(name, viewnames)
    _context.action(
        discriminator = ('view', for_, name, request_type, IView),
        callable = handler,
        args = ('registerAdapter',
                viewgroup, (for_, request_type), IView, name,
                _context.info),
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

    request_type = GlobalObject(
        title=u"""The request type interface for the viewgroup""",
        description=(u"The viewgroup will be called if the interface "
                     u"represented by 'request_type' is implemented by the "
                     u"request.  The default request type is "
                     u"'repoze.bfg.interfaces.IRequest'"),
        required=False
        )
