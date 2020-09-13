from typing import Union, Sequence

from django.conf import settings
from django.core.management.base import BaseCommand

from core.helpers import iterable_to_map
from sales.models import Association
from payment.services.payutc_client import PayutcClient


class Command(BaseCommand):
    """
    Fetch fun_ids and attach these to the related associations

    Usage:
        python manage.py fetch_fun_ids
    """

    help = "Fetch fun_ids and attach these to the related associations."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--report_matched",
                            action="store_true",
                            help="Add matched report to output")
        parser.add_argument("--report_missed",
                            action="store_true",
                            help="Add missed report to output")
        parser.add_argument("--report",
                            action="store_true",
                            help="Add matched and missed report to output")

    @staticmethod
    def patch_name(name: Union[Association, str]) -> str:
        """
        Patch association and fundation names for better match
        """
        if isinstance(name, Association):
            name = name.shortname
        return name.lower().replace("'", "").replace(" ", "")

    @staticmethod
    def report(name: Union[Association, str], data: Sequence[str],
               report_data: bool, report: bool) -> str:
        if not report_data and not report:
            return ""
        return f"\n{name}ed:" + ("".join(data) if data else f"No {name.lower()}")

    def handle(self,
               report: bool=False,
               report_matched: bool=False,
               report_missed: bool=False,
               **options) -> str:
        """
        Fetch fun_ids and attach these to the related associations
        """
        payutc = PayutcClient(settings.PAYUTC)
        payutc.login_app()
        payutc.login_user()

        # Fetch fundations from Payutc and associations from Portail
        fundations = payutc.get_fundations()
        associations = Association.objects.get_with_api_data()
        associations = iterable_to_map(associations, get_key=self.patch_name)

        matched, missed = [], []
        for fundation in fundations:
            asso = associations.pop(self.patch_name(fundation["name"]), None)
            if asso:
                matched.append(f"\n - {fundation['id']}: {fundation['name']} = {asso.shortname}")
                asso.fun_id = fundation["id"]
                asso.save()
            else:
                missed.append(f"\n - {fundation['id']}: {fundation['name']}")

        return f"Fetched {len(fundations)} fundations " \
               + f"and {len(associations)} associations " \
               + f"and matched {len(matched)}" \
               + self.report("Match", matched, report_matched, report) \
               + self.report("Miss", missed, report_missed, report)
