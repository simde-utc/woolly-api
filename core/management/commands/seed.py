from django.core.management.base import BaseCommand

from core.faker import FakeModelFactory, MODELS_MAP


MODELS_CHAINS = {
    'sale': ['itemgroup', 'item'],
    'itemgroup': ['item'],
    'order': ['orderline'],
    'orderline': ['orderlineitem'],
}


class Command(BaseCommand):
    """
    Seed fake models into the database

    Usage:
        python manage.py seed --help
    """

    help = "Seed fake models into the database."
    faker = FakeModelFactory()

    def add_arguments(self, parser) -> None:
        parser.add_argument('model',
                            choices=tuple(MODELS_MAP),
                            help="Which model to generate")
        parser.add_argument('-n', '--number',
                            type=int,
                            default=1,
                            help="Number of models to generate")
        parser.add_argument('-s', '--simple',
                            action='store_true',
                            default=False,
                            help="Simply create the specified model, not the full chain")

        # Related model specification
        for model in MODELS_MAP:
            parser.add_argument(f'--{model}',
                                default=None,
                                help=f"Model {model} to use as related model")

    def process_options(self, init_kwargs: dict) -> dict:
        kwargs = {}
        for key, value in init_kwargs.items():
            if key in MODELS_MAP and value is not None:
                Model = MODELS_MAP[key]
                kwargs[key] = Model.objects.get(pk=value)
        return kwargs

    def create(self, model: str, number: int=1) -> list:

        created_models = []
        Model = MODELS_MAP[model]

        # Create models one by one to have integrety
        # between two models requiring the same superior model
        for _ in range(number):
            # Create model
            data = self.faker.create(Model, **self.kwargs)

            # Add model to store
            self.models[model].add(data)
            self.kwargs[model] = data
            created_models.append(data)

            # Add relative models to store
            for field in data._meta.get_fields():
                if field.is_relation:
                    # Add relation to store
                    key = field.related_model.__name__.lower()
                    if field.many_to_many or field.one_to_many:
                        for method in ('get_attname', 'get_accessor_name'):
                            if hasattr(field, method):
                                name = getattr(field, method)()
                                for related_data in getattr(data, name).all():
                                    if related_data is not None:
                                        self.models[key].add(related_data)
                                break
                    else:
                        related_data = getattr(data, field.name)
                        if related_data is not None:
                            self.models[key].add(related_data)

                    # Update kwargs with last model
                    if self.models[key]:
                        self.kwargs[key] = next(iter(self.models[key]))

        return created_models

    def display_models(self, key: str) -> str:
        n = len(self.models[key])
        return f"{n:2d} {MODELS_MAP[key].__name__}" + ('s' if n > 1 else '')

    def handle(self, model: str, number: int=1, simple: bool=True, **options) -> str:
        if model not in MODELS_MAP:
            raise ValueError(f"Model {model} does not exist.")
        if number < 1:
            raise ValueError(f"Must create at least one model")

        self.models = { key: set() for key in MODELS_MAP }
        self.kwargs = self.process_options(options)

        # Simple creation
        if simple:
            self.create(model, number)
        # Chained creation
        else:
            chain = [ model ] * number
            model = None
            while chain:
                # Create model and extend chain
                model = chain.pop()
                self.create(model)
                chain += MODELS_CHAINS.get(model, [])

        # Display created results
        results = [
            f"\n- {self.display_models(key):20s} {[ m.pk for m in models ]}"
            for key, models in self.models.items() if models
        ]
        return f"Created or used:{''.join(results)}"
