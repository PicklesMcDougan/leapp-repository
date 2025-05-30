from leapp.models import fields, Model
from leapp.topics import SystemInfoTopic


class EnvVar(Model):
    topic = SystemInfoTopic

    name = fields.String()
    """Name of the environment variable."""

    value = fields.String()
    """Value of the environment variable."""


class OSRelease(Model):
    topic = SystemInfoTopic

    release_id = fields.String()
    name = fields.String()
    pretty_name = fields.String()
    version = fields.String()
    version_id = fields.String()
    variant = fields.Nullable(fields.String())  # isn't specified on some systems
    variant_id = fields.Nullable(fields.String())  # same as above


class Version(Model):
    topic = SystemInfoTopic

    source = fields.String()
    """Version of the source (current) system. E.g.: '7.8'."""

    target = fields.String()
    """Version of the target system. E.g. '8.2.'."""

    virtual_source_version = fields.String()
    """
    Source OS version used when checking whether to execute version-dependent code.

    On RHEL and other systems that have version of the form MINOR.MAJOR, `virtual_source_version`
    matches `source_version`.

    CentOS has version of the form MAJOR, lacking the minor version number. The
    `virtual_source_version` value is obtained by combining CentOS major
    version number with a minor version number stored internally in the upgrade_paths.json file.
    """

    virtual_target_version = fields.String()
    """ See :py:attr:`virtual_source_version` """


class IPUSourceToPossibleTargets(Model):
    """
    Represents upgrade paths from a source system version.

    This model is not supposed to be produced nor consumed directly by any actor.
    """
    topic = SystemInfoTopic

    source_version = fields.String()
    """Source system version."""

    target_versions = fields.List(fields.String())
    """List of defined target system versions for the `source_version` system."""


class IPUConfig(Model):
    """
    IPU workflow configuration model
    """
    topic = SystemInfoTopic

    leapp_env_vars = fields.List(fields.Model(EnvVar), default=[])
    """Environment variables related to the leapp."""

    os_release = fields.Model(OSRelease)
    """Data about the OS get from /etc/os-release."""

    version = fields.Model(Version)
    """Version of the current (source) system and expected target system."""

    architecture = fields.String()
    """Architecture of the system. E.g.: 'x86_64'."""

    kernel = fields.String()
    """
    Originally booted kernel when on the source system.
    """

    flavour = fields.StringEnum(('default', 'saphana'), default='default')
    """Flavour of the upgrade - Used to influence changes in supported source/target release"""

    supported_upgrade_paths = fields.List(fields.Model(IPUSourceToPossibleTargets))
    """
    List of supported upgrade paths.

    The list contains only upgrade paths for the `flavour` of the source system.
    """
