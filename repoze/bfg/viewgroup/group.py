import itertools

from webob import Response

from repoze.bfg.exceptions import Forbidden
from repoze.bfg.view import render_view_to_iterable
from repoze.bfg.view import render_view

class ViewGroup(object):
    def __init__(self, name, viewnames):
        self.name = name
        self.viewnames = viewnames

    def __call__(self, context, request):
        renderings = []

        for viewname in self.viewnames:
            try:
                iterable = render_view_to_iterable(context, request, viewname)
            except Forbidden:
                continue
            if iterable is None:
                raise ValueError(
                    'No such view named %s for viewgroup %s' %
                    (viewname, self.name)
                    )
            renderings.append(iterable)

        return Response(app_iter=itertools.chain(*renderings))

class Provider(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, name='', secure=True):
        return render_view(self.context, self.request, name, secure)
    
