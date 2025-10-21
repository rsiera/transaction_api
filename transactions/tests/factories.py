import factory
import factory.django as django_factory
from django.contrib.auth.models import User

from ..models import FileImportRequest, Transaction


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    is_staff = False
    is_superuser = False


class FileImportRequestFactory(django_factory.DjangoModelFactory):
    class Meta:
        model = FileImportRequest

    file = factory.django.FileField(filename="transactions.csv")
    requested_by = factory.SubFactory(UserFactory)


class TransactionFactory(django_factory.DjangoModelFactory):
    class Meta:
        model = Transaction
