import itertools

from zope.interface import implements

from webob import Response

from repoze.bfg.interfaces import IView
from repoze.bfg.security import Unauthorized
from repoze.bfg.view import render_view_to_iterable

class ViewGroup(object):
    implements(IView)
    
    def __init__(self, name, viewnames):
        self.name = name
        self.viewnames = viewnames

    def __call__(self, context, request):
        renderings = []

        for viewname in self.viewnames:
            try:
                iterable = render_view_to_iterable(context, request, viewname)
            except Unauthorized:
                continue
            if iterable is None:
                raise ValueError(
                    'No such view named %s for viewgroup %s' %
                    (viewname, self.name)
                    )
            renderings.append(iterable)

        return Response(app_iter=itertools.chain(*renderings))

