from leapp import reporting
from leapp.libraries.stdlib import api
from leapp.libraries.stdlib.config import is_verbose
from leapp.models import InstalledUnsignedRPM


def generate_report(packages):
    """ Generate a report if there are unsigned packages installed on the system """
    if not packages:
        return
    unsigned_packages_new_line = '\n'.join(['- ' + p for p in packages])
    title = 'Packages not signed by Red Hat found on the system'
    summary = ('The following packages have not been signed by Red Hat'
               ' and may be removed during the upgrade process in case Red Hat-signed'
               ' packages to be removed during the upgrade depend on them:\n{}'
               .format(unsigned_packages_new_line))
    hint = (
        'The most simple solution that does not require additional knowledge'
        ' about the upgrade process'
        ' is the uninstallation of such packages before the upgrade and'
        ' installing these (or their newer versions compatible with the target'
        ' system) back after the upgrade. Also you can just try to upgrade the'
        ' system on a testing machine (or after the full system backup) to see'
        ' the result.\n'
        'However, it is common use case to migrate or upgrade installed third'
        ' party packages together with the system during the in-place upgrade'
        ' process. To examine how to customize the process to deal with such'
        ' packages, follow the documentation in the attached link'
        ' for more details.'
    )
    reporting.create_report([
        reporting.Title(title),
        reporting.Summary(summary),
        reporting.Severity(reporting.Severity.HIGH),
        reporting.Groups([reporting.Groups.SANITY]),
        reporting.Remediation(hint=hint),
        reporting.ExternalLink(
            url='https://red.ht/customize-rhel-upgrade-actors',
            title='Handling the migration of your custom and third-party applications'
        )
    ])

    if is_verbose():
        api.show_message(summary)


def get_unsigned_packages():
    """ Get list of unsigned packages installed in the system """
    rpm_messages = api.consume(InstalledUnsignedRPM)
    data = next(rpm_messages, InstalledUnsignedRPM())
    if list(rpm_messages):
        api.current_logger().warning('Unexpectedly received more than one InstalledUnsignedRPM message.')
    unsigned_packages = set()
    unsigned_packages.update([pkg.name for pkg in data.items])
    unsigned_packages = list(unsigned_packages)
    unsigned_packages.sort()
    return unsigned_packages


def check_unsigned_packages():
    """ Check and generate reports if system contains unsigned installed packages"""
    generate_report(get_unsigned_packages())
