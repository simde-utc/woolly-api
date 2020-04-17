from typing import List

from django.core.management.base import BaseCommand, CommandError

from core.faker import MODELS_MAP

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
            'name': "Prénom",
            'type': "string",
            'default': "owner.first_name",
        },
        {
            'name': "Nom",
            'type': "string",
            'default': "owner.last_name",
        },
        {
            'name': "Sexe",
            'type': "choices",
            'default': "H,F",
        },
        {
            'name': "Date de naissance",
            'type': "date",
            'default': None,
        },
        {
            'name': "Numéro de téléphone",
            'type': "tel",
            'default': None,
        },
        {
            'name': "Login CAS",
            'type': "string",
            'default': None,
        },
        {
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
