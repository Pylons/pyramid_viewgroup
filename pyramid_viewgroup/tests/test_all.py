import unittest

from zope.interface import Interface
from zope.interface import implements

from pyramid import testing
from pyramid.interfaces import IResponse
from pyramid.config import Configurator

class TestViewGroupDirective(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_zcml')
        self.config.hook_zca()

    def tearDown(self):
        self.config.end()

    def _getFUT(self):
        from pyramid_viewgroup.zcml import viewgroup
        return viewgroup

    def test_no_viewnames(self):
        f = self._getFUT()
        from zope.configuration.exceptions import ConfigurationError
        context = DummyContext()
        self.assertRaises(ConfigurationError, f, context)

    def test_call(self):
        from pyramid.registry import Registry
        from pyramid.interfaces import IView
        from pyramid.interfaces import IRequest
        f = self._getFUT()
        context = DummyContext()
        context.registry = Registry()
        context.registry.settings = {}
        context.package = None
        context.autocommit = True
        context.config_class = Configurator
        context.basepath = ''
        context.includepath = ''
        context.route_prefix = ''
        context.introspection = True
        class IFoo:
            pass
        def view(context, request):
            """ """
        f(context, 'viewgroup', ['a', 'b', 'c'], IFoo)

        reg = self.config.registry
        wrapper = reg.adapters.lookup((IRequest, Interface), IView,
                                      name='viewgroup')
        self.assertEqual(wrapper, None)

class TestViewGroup(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_zcml')
        self.config.begin()
        self.config.hook_zca()

    def tearDown(self):
        self.config.end()

    def _getTargetClass(self):
        from pyramid_viewgroup import ViewGroup
        return ViewGroup

    def _registerSecurityPolicy(self):
        self.config.testing_securitypolicy()

    def _registerView(self, view, name):
        self.config.add_view(view, name=name)

    def _makeOne(self, name, viewnames):
        return self._getTargetClass()(name, viewnames)

    def test_no_viewnames(self):
        group = self._makeOne('viewgroup', [])
        context = DummyContext()
        request = DummyRequest()
        response = group(context, request)
        self.assertEqual(''.join(response.app_iter), '')

    def test_viewname_not_found(self):
        self._registerSecurityPolicy()

        group = self._makeOne('viewgroup', ['view1'])
        context = DummyContext()
        request = DummyRequest()
        self.assertRaises(ValueError, group, context, request)

    def test_all_permitted(self):
        self._registerSecurityPolicy()

        response1 = DummyResponse()
        response1.app_iter = ['Response1']
        view1 = make_view(response1)
        self._registerView(view1, 'view1')

        response2 = DummyResponse()
        response2.app_iter = ['Response2']
        view2 = make_view(response2)
        self._registerView(view2, 'view2')

        group = self._makeOne('viewgroup', ['view1', 'view2'])
        context = DummyContext()
        request = DummyRequest()
        request.registry = self.config.registry
        response = group(context, request)
        self.assertEqual(''.join(response.app_iter), 'Response1Response2')

    def test_one_notpermitted(self):
        from pyramid.exceptions import Forbidden
        self._registerSecurityPolicy()

        def view1(context, request):
            raise Forbidden
        self._registerView(view1, 'view1')

        response2 = DummyResponse()
        response2.app_iter = ['Response2']
        view2 = make_view(response2)
        self._registerView(view2, 'view2')

        group = self._makeOne('viewgroup', ['view1', 'view2'])
        context = DummyContext()
        request = DummyRequest()
        request.registry = self.config.registry
        response = group(context, request)
        self.assertEqual(''.join(response.app_iter), 'Response2')

class TestProvider(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_zcml')
        self.config.hook_zca()

    def tearDown(self):
        self.config.end()

    def _getTargetClass(self):
        from pyramid_viewgroup import Provider
        return Provider

    def _makeOne(self, context, request):
        return self._getTargetClass()(context, request)

    def _registerView(self, view, name, **kw):
        self.config.add_view(view, name=name, **kw)

    def test_call(self):
        response1 = DummyResponse()
        response1.app_iter = ['Response1']
        view1 = make_view(response1)
        self._registerView(view1, 'view1')

        response2 = DummyResponse()
        response2.app_iter = ['Response2']
        view2 = make_view(response2)
        self._registerView(view2, 'view2')

        from pyramid_viewgroup import ViewGroup

        group = ViewGroup('viewgroup', ['view1', 'view2'])
        self._registerView(group, 'viewgroup')

        context = DummyContext()
        request = DummyRequest()
        request.registry = self.config.registry 
        provider = self._makeOne(context, request)
        self.assertEqual(provider('view1'), 'Response1')
        self.assertEqual(provider('view2'), 'Response2')
        self.assertEqual(provider('viewgroup'), 'Response1Response2')

class Test_includeme(unittest.TestCase):
    def _callFUT(self, config):
        from pyramid_viewgroup import includeme
        includeme(config)

    def test_it(self):
        from pyramid_viewgroup import add_viewgroup
        config = DummyConfigurator()
        self._callFUT(config)
        self.assertEqual(config.add_viewgroup, add_viewgroup)


class TestFixtureApp(unittest.TestCase):
    def setUp(self):
        from pyramid.config import Configurator
        from pyramid_viewgroup.tests import fixtureapp
        self.config = Configurator(package=fixtureapp, autocommit=True)
        self.config.include('pyramid_zcml')
        self.config.hook_zca()

    def tearDown(self):
        self.config.end()

    def test_it(self):
        self.config.load_zcml('configure.zcml')

class DummyRequest:
    from zope.interface import implements
    from pyramid.interfaces import IRequest
    implements(IRequest)

class DummyContext:
    pass

class DummySecurityPolicy:
    pass

class Dummy:
    pass

class DummyConfigurator(object):
    def add_directive(self, name, directive):
        self.__dict__[name] = directive
        
class DummyContext:
    package = None

    def __init__(self):
        self.actions = []
        self.info = None

class IDummy(Interface):
    pass

    
class DummyResponse:
    implements(IResponse)
    status = '200 OK'
    headerlist = ()
    app_iter = ()
    
def make_view(response):
    def view(context, request):
        return response
    return view

