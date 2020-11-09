from typing import List

from django.core.management.base import BaseCommand, CommandError

from authentication.models import UserType
from sales.models import Field


MODELS_MAP = {
    'usertype': UserType,
    'field': Field,
}

DEFAULTS = {
    'usertype': [
        {
            'id': 'cotisant_bde',
            'name': 'Cotisant BDE',
            'validation': 'user.fetched_data["types"]["contributorBde"]',
        },
        {
            'id': 'utc',
            'name': 'UTC',
            'validation': 'user.fetched_data["types"]["cas"]',
        },
        {
            'id': 'tremplin',
            'name': 'Tremplin UTC',
            'validation': 'user',
        },
        {
            'id': 'exterieur',
            'name': 'Extérieur',
            'validation': 'True',
        },
    ],
    'field': [
        {
            'id': "first_name",
            'name': "Prénom",
            'type': "string",
            'default': "owner.first_name",
        },
        {
            'id': "last_name",
            'name': "Nom",
            'type': "string",
            'default': "owner.last_name",
        },
        {
            'id': "sex",
            'name': "Sexe",
            'type': "choices",
            'default': "H,F",
        },
        {
            'id': "birthdate",
            'name': "Date de naissance",
            'type': "date",
            'default': None,
        },
        {
            'id': "telnumber",
            'name': "Numéro de téléphone",
            'type': "tel",
            'default': None,
        },
        {
            'id': "cas_login",
            'name': "Login CAS",
            'type': "string",
            'default': None,
        },
        {
            'id': "is_adulte",
            'name': "Adulte ?",
            'type': "boolean",
            'default': True,
        },
    ]
}


class Command(BaseCommand):
    """
    Initialize the different models defaults values in the database

    Usage:
        python manage.py list_ids.py --help
    """

    help = "Initialize the different models defaults values in the database."

    def add_arguments(self, parser) -> None:
        parser.add_argument('models',
                            nargs='*',
                            default=['all'],
                            choices=tuple(['all', *DEFAULTS]),
                            help="Which model to generate")

    def handle(self, models: List[str], **options) -> str:
        """
        Initialize the different default UserTypes in DB
        """
        if 'all' in models:
            if len(models) > 1:
                raise CommandError("Need either 'all' or a list of models but not both")
            models = DEFAULTS.keys()

        results = {}
        for key in models:
            Model = MODELS_MAP[key]
            results[Model] = { 'Created': [], 'Skipped': [] }

            # Create default instances and add result to store
            for data in DEFAULTS[key]:
                pk = data.pop('id', None)
                if pk:
                    has_created = Model.objects.get_or_create(defaults=data, pk=pk)[1]
                    results[Model]['Created' if has_created else 'Skipped'].append(str(pk))
                else:
                    pk = Model.objects.create(**data).pk
                    results[Model]['Created'].append(str(pk))

        text = []
        for Model, store in results.items():
            text.append(f"{Model.__name__}:")
            for key, ids in store.items():
                text.append(f"- {key} {len(ids)}: {', '.join(ids)}")
        return '\n'.join(text)
