"""Shared Plone test layers for eea.coremetadata."""

from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.testing import z2


class EEACoreMetadataFixture(PloneSandboxLayer):
    """Install eea.coremetadata in an isolated Plone site."""

    def setUpZope(self, app, configurationContext):
        """Load package configuration and required Zope products."""
        import collective.taxonomy
        import eea.coremetadata

        self.loadZCML(package=collective.taxonomy)
        z2.installProduct(app, "collective.taxonomy")
        self.loadZCML(package=eea.coremetadata)
        z2.installProduct(app, "eea.coremetadata")

    def setUpPloneSite(self, portal):
        """Install the default profile and grant test manager access."""
        applyProfile(portal, "eea.coremetadata:default")
        setRoles(portal, TEST_USER_ID, ["Manager"])

    def tearDownZope(self, app):
        """Remove the package product after the layer is torn down."""
        z2.uninstallProduct(app, "eea.coremetadata")


EEA_COREMETADATA_FIXTURE = EEACoreMetadataFixture()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(EEA_COREMETADATA_FIXTURE,),
    name="EEACoreMetadata:Integration",
)

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(EEA_COREMETADATA_FIXTURE,),
    name="EEACoreMetadata:Functional",
)
