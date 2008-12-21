import unittest

from zope.component.testing import PlacelessSetup
from zope.interface import Interface

class TestViewGroupDirective(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _getFUT(self):
        from repoze.bfg.viewgroup.zcml import viewgroup
        return viewgroup

    def test_no_viewnames(self):
        f = self._getFUT()
        from zope.configuration.exceptions import ConfigurationError
        context = DummyContext()
        self.assertRaises(ConfigurationError, f, context)

    def test_only_viewnames(self):
        f = self._getFUT()
        context = DummyContext()
        f(context, 'viewgroup', ['a', 'b', 'c'])
        actions = context.actions
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.viewgroup.zcml import handler

        self.assertEqual(len(actions), 1)

        regadapt = actions[0]
        regadapt_discriminator = ('view', None, 'viewgroup', IRequest, IView)
        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        self.assertEqual(regadapt['args'][1].name, 'viewgroup')
        self.assertEqual(regadapt['args'][1].viewnames, ['a', 'b', 'c'])
        self.assertEqual(regadapt['args'][2], (None, IRequest))
        self.assertEqual(regadapt['args'][3], IView)
        self.assertEqual(regadapt['args'][4], 'viewgroup')
        self.assertEqual(regadapt['args'][5], None)

    def test_with_request_type(self):
        f = self._getFUT()
        context = DummyContext()
        class IFoo:
            pass
        def view(context, request):
            pass
        f(context, 'viewgroup', ['a', 'b', 'c'], IFoo, request_type=IDummy)
        actions = context.actions
        from repoze.bfg.interfaces import IView
        from repoze.bfg.viewgroup.zcml import handler
        from zope.component.interface import provideInterface

        self.assertEqual(len(actions), 2)

        provide = actions[0]
        self.assertEqual(provide['discriminator'], None)
        self.assertEqual(provide['callable'], provideInterface)
        self.assertEqual(provide['args'][0], '')
        self.assertEqual(provide['args'][1], IFoo)

        regadapt = actions[1]
        regadapt_discriminator = ('view', IFoo, 'viewgroup', IDummy, IView)
        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        self.assertEqual(regadapt['args'][1].name, 'viewgroup')
        self.assertEqual(regadapt['args'][1].viewnames, ['a', 'b', 'c'])
        self.assertEqual(regadapt['args'][2], (IFoo, IDummy))
        self.assertEqual(regadapt['args'][3], IView)
        self.assertEqual(regadapt['args'][4], 'viewgroup')
        self.assertEqual(regadapt['args'][5], None)

class TestViewGroup(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _getTargetClass(self):
        from repoze.bfg.viewgroup.group import ViewGroup
        return ViewGroup

    def _registerSecurityPolicy(self, secpol):
        import zope.component
        gsm = zope.component.getGlobalSiteManager()
        from repoze.bfg.interfaces import ISecurityPolicy
        gsm.registerUtility(secpol, ISecurityPolicy)

    def _registerView(self, app, name, *for_):
        import zope.component
        gsm = zope.component.getGlobalSiteManager()
        from repoze.bfg.interfaces import IView
        gsm.registerAdapter(app, for_, IView, name)

    def _makeOne(self, name, viewnames):
        return self._getTargetClass()(name, viewnames)

    def test_no_viewnames(self):
        secpol = DummySecurityPolicy()
        self._registerSecurityPolicy(secpol)
        group = self._makeOne('viewgroup', [])
        context = DummyContext()
        request = DummyRequest()
        response = group(context, request)
        self.assertEqual(''.join(response.app_iter), '')

    def test_viewname_not_found(self):
        secpol = DummySecurityPolicy()
        self._registerSecurityPolicy(secpol)

        group = self._makeOne('viewgroup', ['view1'])
        context = DummyContext()
        request = DummyRequest()
        self.assertRaises(ValueError, group, context, request)

    def test_all_permitted(self):
        secpol = DummySecurityPolicy()
        self._registerSecurityPolicy(secpol)

        response1 = DummyResponse()
        response1.app_iter = ['Response1']
        view1 = make_view(response1)
        self._registerView(view1, 'view1', None, None)

        response2 = DummyResponse()
        response2.app_iter = ['Response2']
        view2 = make_view(response2)
        self._registerView(view2, 'view2', None, None)

        group = self._makeOne('viewgroup', ['view1', 'view2'])
        context = DummyContext()
        request = DummyRequest()
        response = group(context, request)
        self.assertEqual(''.join(response.app_iter), 'Response1Response2')

class TestProvider(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _getTargetClass(self):
        from repoze.bfg.viewgroup.group import Provider
        return Provider

    def _makeOne(self, context, request):
        return self._getTargetClass()(context, request)

    def _registerView(self, app, name, *for_):
        import zope.component
        gsm = zope.component.getGlobalSiteManager()
        from repoze.bfg.interfaces import IView
        gsm.registerAdapter(app, for_, IView, name)

    def test_call(self):
        response1 = DummyResponse()
        response1.app_iter = ['Response1']
        view1 = make_view(response1)
        self._registerView(view1, 'view1', None, None)

        response2 = DummyResponse()
        response2.app_iter = ['Response2']
        view2 = make_view(response2)
        self._registerView(view2, 'view2', None, None)

        from repoze.bfg.viewgroup.group import ViewGroup

        group = ViewGroup('viewgroup', ['view1', 'view2'])
        self._registerView(group, 'viewgroup', None, None)

        context = DummyContext()
        request = DummyRequest()
        provider = self._makeOne(context, request)
        self.assertEqual(provider('view1'), 'Response1')
        self.assertEqual(provider('view2'), 'Response2')
        self.assertEqual(provider('viewgroup'), 'Response1Response2')

class TestFixtureApp(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def test_registry_actions_can_be_pickled_and_unpickled(self):
        import repoze.bfg.viewgroup.tests.fixtureapp as package
        from zope.configuration import config
        from zope.configuration import xmlconfig
        context = config.ConfigurationMachine()
        xmlconfig.registerCommonDirectives(context)
        context.package = package
        xmlconfig.include(context, 'configure.zcml', package)
        context.execute_actions(clear=False)
        actions = context.actions
        import cPickle
        dumped = cPickle.dumps(actions, -1)
        new = cPickle.loads(dumped)
        self.assertEqual(len(actions), len(new))

class DummyRequest:
    pass

class DummyContext:
    pass

class DummySecurityPolicy:
    pass

class Dummy:
    pass

class DummyContext:
    def __init__(self):
        self.actions = []
        self.info = None

    def path(self, name):
        import os
        here = os.path.dirname(__file__)
        fixtures = os.path.join(here, 'fixtures')
        return os.path.join(fixtures, name)

    def action(self, discriminator, callable, args):
        self.actions.append(
            {'discriminator':discriminator,
             'callable':callable,
             'args':args}
            )

class IDummy(Interface):
    pass

    
class DummyResponse:
    status = '200 OK'
    headerlist = ()
    app_iter = ()
    
def make_view(response):
    def view(context, request):
        return response
    return view

