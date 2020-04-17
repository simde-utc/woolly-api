from typing import List

from django.core.management.base import BaseCommand

from core.faker import MODELS_MAP


class Command(BaseCommand):
    """
    Get list of ids of a model from the database

    Usage:
        python manage.py list_ids.py --help
    """

    help = "Get list of ids of a model from the database."

    def add_arguments(self, parser) -> None:
        parser.add_argument('models',
                            nargs='+',
                            choices=tuple(MODELS_MAP),
                            help="Which model to generate")
        parser.add_argument('-l', '--limit',
                            type=int,
                            default=None,
                            help="Limit of ids to display")
        parser.add_argument('-o', '--offset',
                            type=int,
                            default=None,
                            help="Offset of ids to display")

    def handle_model(self, model: str, offset: int=None, limit: int=None) -> str:
        Model = MODELS_MAP[model]
        query = Model.objects.all()
        if offset or limit:
            query = query[slice(offset, limit)]

        if not query:
            return f"No {model} found"

        list_ids = ''.join(f"\n- {data.pk} : {data}" for data in query)
        return f"Found {len(query)} {model}s:{list_ids}"

    def handle(self, models: List[str], offset: int=None, limit: int=None, **options) -> str:
        results = [
            self.handle_model(model, offset, limit) for model in models
        ]
        return '\n'.join(results)
