from typing import Union, List, Dict, Any
from datetime import datetime

from faker import Faker
from django.db.models import Model

from core.helpers import format_date
from authentication.models import User, UserType
from sales.models import (
    Association, Sale, ItemGroup, Item,
    Order, OrderStatus, OrderLine, OrderLineItem,
    Field, ItemField, OrderLineField
)

Pk = Union[str, int, 'UUID']

MODELS = (
    User, UserType, Association, Sale, ItemGroup, Item,
    Order, OrderStatus, OrderLine, OrderLineItem,
    Field, ItemField, OrderLineField
)

MODELS_MAP = { Model.__name__.lower(): Model for Model in MODELS }


class FakeModelFactory:
    """
    Factory that generates instances of specified models filled with fake values.
    Useful for testing purposes.
    """

    def __init__(self, seed: int=None):
        self.faker = Faker()
        if seed is not None:
            self.faker.seed(seed)

    def create(self, model: Model, nb: int=None, **kwargs) -> Union[Model, List[Model]]:
        """
        Generates one or multiple instances of a specified Model

        Args:
            model: the Model class to generate
            nb: the number of instances to generate,
                None returns a single instance (default: None)
            **kwargs: the fixed attributes for the models

        Returns:
            Union[Model, List[Model]]: one or multiple generated instances of Model
        """
        # Return a single model
        if nb is None:
            props = self.get_attributes(model, **kwargs)
            return model.objects.create(**props)
        # Or a list of models
        else:
            if type(nb) is not int or nb <= 0:
                raise ValueError("Number of instances to generate must be greater than 0")
            return [
                model.objects.create(**self.get_attributes(model, **kwargs))
                for __ in range(nb)
            ]

    def get_attributes(self, model: Model, **kwargs) -> Dict[str, Any]:
        """
        Generates the attributes required to create a specified Model

        Args:
            model (Model): the Model whose attributes are to be created
            kwargs: fixed attributes

        Returns:
            Dict[str, Any]: the attributes generated

        Raises:
            NotImplementedError: in case the model is not implemented
        """

        def get_related_model(key: str, _model: Model=None) -> Union[Pk, Model]:
            """
            Helper to get or create a related Model

            Args:
                key: the key to the related model in the kwargs
                model (Model): the type of model to create as a fallback

            Returns:
                Union[Pk, Model]: the model or its primary key
            """
            if key in kwargs:
                return kwargs[key]
            elif _model is not None:
                return self.create(_model)
            else:
                return None

        def get_datetime(key: str, when: str) -> datetime:
            return format_date(kwargs.get(key, self.faker.date_time_this_year(
                before_now=(when == 'before'),
                after_now=(when == 'after'),
            )))

        # ============================================
        #   Authentication
        # ============================================

        if model == User:
            return {
                'id':         kwargs.get('id',         self.faker.uuid4()),
                'email':      kwargs.get('email',      self.faker.email()),
                'first_name': kwargs.get('first_name', self.faker.first_name()),
                'last_name':  kwargs.get('last_name',  self.faker.last_name()),
                'is_admin':   kwargs.get('is_admin',   False),
            }

        if model == UserType:
            return {
                'id':   kwargs.get('id',   self.faker.uuid4()[:25]),
                'name': kwargs.get('name', self.faker.sentence(nb_words=4)),
                'validation': kwargs.get('validation', 'False'),
            }

        # ============================================
        #   Association & Sale
        # ============================================

        if model == Association:
            return {
                'id':        kwargs.get('id',      self.faker.uuid4()),
                'shortname': kwargs.get('name',    self.faker.company()),
                'fun_id':    kwargs.get('fun_id',  self.faker.random_digit()),
            }

        if model == Sale:
            return {
                'id':           kwargs.get('id',          self.faker.slug()),
                'name':         kwargs.get('name',        self.faker.company()),
                'description':  kwargs.get('description', self.faker.paragraph()),
                'association':  get_related_model('association', Association),
                'is_active':    kwargs.get('is_active', True),
                'is_public':    kwargs.get('is_public', True),
                'begin_at':     get_datetime('begin_at', 'before'),
                'end_at':       get_datetime('end_at', 'after'),
                'max_item_quantity': kwargs.get('max_item_quantity', self.faker.random_int()),
            }

        # ============================================
        #   Item & ItemGroup
        # ============================================

        if model == ItemGroup:
            return {
                'name':         kwargs.get('name',         self.faker.word()),
                'sale':         get_related_model('sale',  Sale),
                'is_active':    kwargs.get('is_active',    True),
                'quantity':     kwargs.get('quantity',     self.faker.random_int()),
                'max_per_user': kwargs.get('max_per_user', self.faker.random_int()),
            }

        if model == Item:
            return {
                'name':         kwargs.get('name',         self.faker.word()),
                'description':  kwargs.get('description',  self.faker.paragraph()),
                'sale':         get_related_model('sale',       Sale),
                'group':        get_related_model('group',      None),
                'usertype':     get_related_model('usertype',   UserType),
                'quantity':     kwargs.get('quantity',     self.faker.random_int()),
                'max_per_user': kwargs.get('max_per_user', self.faker.random_int()),
                'is_active':    kwargs.get('is_active',    True),
                'price':        float(kwargs.get('price',  self.faker.random_number() / 10.)),
                'nemopay_id':   kwargs.get('nemopay_id',   self.faker.random_int()),
            }

        # ============================================
        #   Order, OrderLine, OrderLineItem
        # ============================================

        if model == Order:
            return {
                'owner':      get_related_model('owner', User),
                'sale':       get_related_model('sale',  Sale),
                'created_at': get_datetime('created_at', 'before'),
                'updated_at': get_datetime('updated_at', 'before'),
                'status': kwargs.get('status', OrderStatus.ONGOING.value),
                'tra_id': kwargs.get('tra_id', self.faker.random_int()),
            }

        if model == OrderLine:
            return {
                'item':     get_related_model('item',   Item),
                'order':    get_related_model('order',  Order),
                'quantity': kwargs.get('quantity', self.faker.random_digit()),
            }

        if model == OrderLineItem:
            return {
                'orderline': get_related_model('orderline', OrderLine),
            }

        # ============================================
        #   Field, ItemField, OrderLineField
        # ============================================

        if model == Field:
            return {
                'name':     kwargs.get('name',    self.faker.word()),
                'type':     kwargs.get('type',    self.faker.word()),
                'default':  kwargs.get('default', self.faker.word()),
            }

        if model == ItemField:
            return {
                'field':    get_related_model('field',  Field),
                'item':     get_related_model('item',   Item),
                'editable': kwargs.get('editable', self.faker.boolean()),
            }

        if model == OrderLineField:
            return {
                'orderlineitem': get_related_model('orderlineitem', OrderLineItem),
                'field':         get_related_model('field', Field),
                'value':         kwargs.get('value',   self.faker.word()),
            }

        raise NotImplementedError(f"The model {model} isn't fakable yet")
