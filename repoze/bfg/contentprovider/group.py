from zope.interface import implements
from zope.component import queryMultiAdapter
from zope.component import queryUtility

from webob import Response

from repoze.bfg.router import isResponse

from repoze.bfg.interfaces import ISecurityPolicy
from repoze.bfg.interfaces import IViewPermission
from repoze.bfg.interfaces import IView

class ViewGroup(object):
    implements(IView)
    
    def __init__(self, name, viewnames):
        self.name = name
        self.viewnames = viewnames

    def __call__(self, context, request):
        rendering = []
        security_policy = queryUtility(ISecurityPolicy)

        for viewname in self.viewnames:
            permission = queryMultiAdapter((context, request), IViewPermission,
                                           name=viewname)
            if permission is not None:
                if not permission(security_policy):
                    continue

            response = queryMultiAdapter((context, request), IView,
                                         name=viewname)
            if response is None:
                raise ValueError(
                    'No such view named %r for %r during viewgroup rendering' %
                    (viewname, (context, request)))

            if not isResponse(response):
                raise ValueError('response from %r was not IResponse: %r' %
                                 (viewname, response))

            rendering.append(''.join(response.app_iter))

        return Response(''.join(rendering))
    
    

        
