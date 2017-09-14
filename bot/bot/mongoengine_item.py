from mongoengine import ValidationError
from scrapy.item import Field, Item, ItemMeta


class MongoengineItemMeta(ItemMeta):

    def __new__(mcs, class_name, bases, attrs):
        cls = super(MongoengineItemMeta, mcs).__new__(mcs, class_name, bases, attrs)
        cls.fields = cls.fields.copy()

        if cls.mongoengine_model:
            cls._model_fields = []
            cls._model_meta = cls.mongoengine_model._meta

            for model_field_name in cls.mongoengine_model._fields:
                if model_field_name not in cls.fields:
                    cls.fields[model_field_name] = Field()

                cls._model_fields.append(model_field_name)

        return cls


class MongoengineItem(Item):

    __metaclass__ = MongoengineItemMeta

    mongoengine_model = None

    def __init__(self, *args, **kwargs):
        super(MongoengineItem, self).__init__(*args, **kwargs)
        self._instance = None
        self._errors = None

    def save(self, commit=True):
        if commit:
            self.instance.save()
        return self.instance

    def is_valid(self, exclude=None):
        self._get_errors(exclude)
        return not bool(self._errors)

    def _get_errors(self, exclude=None):
        if self._errors is not None:
            return self._errors

        self._errors = {}
        if exclude is None:
            exclude = []

        try:
            self.instance.clean_fields(exclude=exclude)
        except ValidationError as e:
            self._errors = e.update_error_dict(self._errors)

        try:
            self.instance.clean()
        except ValidationError as e:
            self._errors = e.update_error_dict(self._errors)

        # uniqueness is not checked, because it is faster to check it when
        # saving object to database. Just beware, that failed save()
        # raises IntegrityError instead of ValidationError.

        return self._errors
    errors = property(_get_errors)

    @property
    def instance(self):
        if self._instance is None:
            modelargs = dict((k, self.get(k)) for k in self._values
                             if k in self._model_fields)
            self._instance = self.mongoengine_model(**modelargs)
        return self._instance
