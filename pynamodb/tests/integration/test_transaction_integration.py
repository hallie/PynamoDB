from datetime import datetime

import config as cfg
from pynamodb.attributes import NumberAttribute, UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.connection.transaction import TransactGet, TransactWrite

from pynamodb.models import Model


class User(Model):
    class Meta:
        region = 'us-east-1'
        table_name = 'pynamodb-ci'
        host = cfg.DYNAMODB_HOST

    user_id = NumberAttribute(hash_key=True)


class BankStatement(Model):

    class Meta:
        region = 'us-east-1'
        table_name = 'pynamodb-ci'
        host = cfg.DYNAMODB_HOST

    user_id = NumberAttribute(hash_key=True)
    balance = NumberAttribute(default=0)


class LineItem(Model):

    class Meta:
        region = 'us-east-1'
        table_name = 'pynamodb-ci'
        host = cfg.DYNAMODB_HOST

    user_id = NumberAttribute(hash_key=True)
    created_at = UTCDateTimeAttribute(default=datetime.now)
    amount = NumberAttribute()
    currency = UnicodeAttribute()


for model in [User, BankStatement, LineItem]:
    if not model.exists():
        print("Creating table for model {0}".format(model.__class__))
        model.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

transact_write = TransactWrite()
print(transact_write._connection.session.get_service_model(service_name='dynamodb')._service_description)
User(1).save(in_transaction=transact_write)
BankStatement(1).save(condition=(BankStatement.user_id.does_not_exist()), in_transaction=transact_write)
transact_write.commit()

transact_get = TransactGet()
User.get(1, in_transaction=transact_get)
BankStatement.get(1, in_transaction=transact_get)
user, statement = transact_get.commit()
