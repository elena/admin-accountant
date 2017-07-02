# -*- coding: utf-8 -*-
from django.db import models
from django.utils.module_loading import import_string
from decimal import Decimal

from subledgers import settings
from ledgers import utils
from entities.models import Entity
from ledgers.models import Account, Transaction


# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #

# Abstract Classes for Subledgers
#
# See detailed discussion:
# http://admin-accounting.blogspot.com.au/2017/06/subledger-generalisation-and-specifics.html

# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #


class Entry(models.Model):

    # *** ABSTRACT CLASS ***

    """ Generalised in case more fields are necessary for subjedgers.

    For use with at least: Sales, Expenses
    """

    transaction = models.OneToOneField('ledgers.Transaction',
                                       blank=True, default="", null=True)

    additional = models.CharField(
        max_length=128, blank=True, default="", null=True)

    class Meta:
        abstract = True

    def __str__(self):
        try:
            return "{} [{}]-- ${} ".format(self.relation.entity.code,
                                           self.transaction.date,
                                           self.transaction.value)
        except AttributeError:
            if self.transaction.note:
                return "{} -- ${} -- {}".format(self.transaction.date,
                                                self.transaction.value,
                                                self.transaction.note)
            else:
                return "{} -- ${}".format(self.transaction.date,
                                          self.transaction.value)

    # Entry specific utilities:

    def get_required(object_name):
        required = set([x for x in settings.FIELDS_TRANSACTION_REQUIRED]
                       + [x for x in settings.OTHER_REQUIRED_FIELDS]
                       + [x for x in settings.OBJECT_SETTINGS[object_name]
                          ['required_fields']])
        return required

    # This is now redundant.
    def check_required(kwargs):
        required_fields = Entry.get_required(kwargs['object_name'])
        for key, value in kwargs.items():
            if key in settings.FIELD_IS_RELATION:
                try:
                    required_fields.remove('relation')
                except KeyError:
                    pass
            if key in required_fields:
                required_fields.remove(key)
        # there shouldn't be any required fields left
        if required_fields:
            raise Exception("Missing fields: {}".format(
                ", ".join(required_fields)))
        else:
            return True

    def get_cls(name):
        """ Input variations (convert to source_str):
        # 1. ModelObject
        # 2. object_name -- valid vanilla name, eg "CreditorInvoice"
        # 3. source_str
        """

        # 1. ModelObject
        try:
            source = utils.get_source(name)
        except:
            pass

        # 2. object_name -- valid vanilla name, eg "CreditorInvoice"
        try:
            source = settings.OBJECT_SETTINGS[name]['source']
        except:
            pass

        # 3. source_str
        try:
            if source in settings.VALID_SOURCES:
                cls = import_string(source)
                return cls
        except UnboundLocalError:
            raise Exception("No valid upload `type` {}.".format(name))
        raise Exception("No valid `type` found for {}.".format(name))

    # Entry process specific utilities:

    def dump_to_objects(dump, user, object_name=None, self=None, live=True):
        """
        ** End-to-End **

        Main function for bringing together the elements of constructing
        the list of kwargs for transactions / invoices based upon whatever is
        required for the object.

        Defining Object type by "object_name":
         Either: batch of same Object Class(using * arg `object_name`)
                 or: by calling method from Object Class(eg. CreditorInvoice)
             or: column header `object_name` defining on a row-by-row basis.

         There is the choice of either preselecting what object_name of
         objects are being defined such as "CreditorInvoice" objects or
        "JournalEntry" objects.

         Alternatively each `row` should define a `object_name`.

        `user` will be added here as the individual creating this list is
        the one who should be tied to the objects.
        """

        # ** Part 1. convert dump to `list` of `dict` objects
        table = utils.tsv_to_dict(dump)

        obj_list = []
        for row_dict in table:

            # flush lines list at the beginning of each loop
            lines = []

            # ** Part 2. Gettings `user` and `cls`
            # copy kwargs to ensure valid set/uniform keys
            kwargs = {k.lower(): v for k, v in row_dict.items()}

            # figure out the `type` for this object
            if kwargs.get('type'):
                cls = Entry.get_cls(row_dict['type'])
            elif object_name:
                cls = Entry.get_cls(object_name)
            elif self:
                cls = Entry.get_cls(self)
            else:
                raise Exception(
                    "No `type` column specified, unable to create objects.")

            # will fail if no relation
            relk = [rel for rel in row_dict
                    if rel in settings.FIELD_IS_RELATION]
            if relk:
                if kwargs[relk[0]]:
                    entity_code = kwargs[relk[0]]
                    kwargs['relation'] = Relation.get_relation_by_entry(
                        entity_code, cls.__name__)
                else:
                    kwargs.pop('relation')

            # 4. find account fields, add lines
            # 4a. find accounts, create line
            # `if` is unnecessary but included for clarity
            for key in row_dict:
                if Account.get_account(key) and row_dict[key]:
                    lines.append((Account.get_account(key),
                                  utils.make_decimal(row_dict[key])))
            kwargs['lines'] = lines

            # ** Part 3. validate_object_kwargs
            kwargs = Entry.validate_object_kwargs(kwargs, user, cls)

            # ** Part 4. create_object
            # passing kwargs as dict not **kwargs
            new_object = Entry.create_object(kwargs, live=live)

            obj_list.append(new_object)

        # Returns list of big dictionaries containing everything dumped in.
        return obj_list

    def make_dicts(kwargs):
        trans_kwargs = {k: kwargs[k]
                        for k in settings.FIELDS_TRANSACTION if kwargs.get(k)}

        object_settings = settings.OBJECT_SETTINGS[kwargs['object_name']]
        obj_kwargs = {k: kwargs[k]
                      for k in object_settings['fields'] if kwargs.get(k)}
        return (trans_kwargs, obj_kwargs)

    def validate_object_kwargs(kwargs, user, cls):
        """ for each line/row:

            1. allocate class

            2. add `source` using ledgers.utils.get_source(`Model`)
                            based upon `Model` provided in object settings
               add `user` from positional arg
               add `object` from positional arg

            3. convert: IS_DATE using dateparser.parse
                        IS_MONEY using ledgers.utils.make_decimal()

            4. create and add `lines` list of tuples:
               4a. find fields that are accounts using Account.get_account(key)
               add (k, v) to `lines`

               4b.
               add `value` (correct CR/DR)
               add `gst_total` [optional, if specified in object settings]

               4c. add `lines` to `kwargs`

        5. check all required fields are represented (or explode)
           append `row_dict` set to `list_kwargs`
        """

        # 1. allocate class
        kwargs['user'] = user
        kwargs['cls'] = cls
        kwargs['object_name'] = object_name = cls.__name__

        # 2. add source
        object_settings = settings.OBJECT_SETTINGS[object_name]
        kwargs['source'] = utils.get_source(object_settings['source'])

        required = {k: "" for k in Entry.get_required(object_name)}
        for key in required:

            # 3. typing
            if key in settings.FIELD_IS_DATE:
                kwargs[key] = utils.make_date(kwargs[key])
            if key in settings.FIELD_IS_DECIMAL:
                kwargs[key] = utils.make_decimal(kwargs[key])

        # 4b. and value and (conditionally) gst_total
        lines = kwargs['lines']

        # @@ TODO facilitate other taxes and surcharges.
        if object_settings.get('is_GST'):

            gst_allocated = False
            for line in lines:
                if line[0] == settings.GST_DR_ACCOUNT\
                   or line[0] == settings.GST_CR_ACCOUNT:
                    gst_allocated = True

            if not gst_allocated:
                # note: correct GST account, abs value
                # fix dr/cr +/- in next process, not here.
                if object_settings.get('is_tb_account_DR'):
                    lines.append((
                        settings.GST_DR_ACCOUNT,
                        utils.make_decimal(kwargs['gst_total'])))
                if object_settings.get('is_tb_account_CR'):
                    lines.append((
                        settings.GST_CR_ACCOUNT,
                        utils.make_decimal(kwargs['gst_total'])))

        if object_settings.get('tb_account'):

            bal = 0
            for i, line in enumerate(lines):
                # Negate if DR:
                if object_settings.get('is_tb_account_DR'):
                    lines[i] = (line[0], -line[1])
                bal += line[1]

            if kwargs['value'] and\
               not Decimal(kwargs['value']) == abs(Decimal(bal)):
                raise Exception('Value provide ({}) does not equal remaining balance: {}'.format(kwargs['value'], bal))  # noqa

            # CR/Liability
            if object_settings.get('is_tb_account_CR'):
                lines.append((
                    object_settings['tb_account'],
                    utils.set_CR(bal)))

            # DR/Asset
            if object_settings.get('is_tb_account_DR'):
                lines.append((
                    object_settings['tb_account'],
                    utils.set_DR(bal)))

            # @@ TODO make a decision about adding Invoice due_date

        # 4c.
        kwargs['lines'] = lines

        # 5 powerful check, will explode if not quite precisely correct
        Entry.check_required(kwargs)

        return kwargs

    def create_object(kwargs, live=True):
        """
        Each :obj:`dict` represents the necessary **kwargs to create an object.

        Can be generated from a spreadsheet dump using `self.dump_to_kwargs`
        providing all the necessary fields are represented.

        # Inception Rules:
          if: called via abstract class `Entry` can be mixed
              `type` column must be specified.

          if: this used via concrete class:
             if `type` column, this will be used to create object
             otherwise: concrete class will be assumed for all objects.

        Defining Object class:
            Either: batch of same Class Object (using *arg `object_name`)
                or: kwarg key `object_name` defined on a row-by-row basis.

        """
        cls = kwargs['cls']
        trans_kwargs, obj_kwargs = Entry.make_dicts(kwargs)  # noqa

        try:
            new_obj = cls(**obj_kwargs)
            new_trans = Transaction(**trans_kwargs)
            if live:
                new_trans.save(lines=kwargs['lines'])
                new_obj.transaction = new_trans
                new_obj.save()
                return new_obj
        except Exception as e:
            """ This line exists to ensure `Transaction` objects are not
            created if there is a validation problem with the `Entry`, as
            `Transaction` must be created before `Entry`.

            This is important for system integrity, until there is some
            generic relation from `Transaction` that we can ensure exists.

            # @@ TODO: This important integrity check needs to be done
            better.

            This should nearly certainly be done as post_save signal
            on Entry. taiga#122
            """
            print("Error {}. Keys provided: {}".format(e, ", ".join(
                obj_kwargs)))
            new_trans.delete()
            return "Error {}: {}".format(e, ", ".join(kwargs))


class Invoice(Entry):

    # *** ABSTRACT CLASS ***

    """ For use with at least: Creditors Invoices, Debtors Invoices

    7 legal components of an invoice: the words "invoice", date, seller,
    seller abn, what, tax (and what applied to), total value, (due date)

    Transaction contains:
    from *abstract* `Entry`
      transaction = models.OneToOneField('ledgers.Transaction')
      - *Date
      - *Value
      - Note
      - *User
      - source
    """

    due_date = models.DateField(null=True)

    invoice_number = models.CharField(max_length=128)

    order_number = models.CharField(
        max_length=128, blank=True, default="", null=True)

    reference = models.CharField(
        max_length=128, blank=True, default="", null=True)

    gst_total = models.DecimalField(
        max_digits=19, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        abstract = True


class Payment(models.Model):

    # *** ABSTRACT CLASS ***
    # *** NOT a Transaction  ***

    """ Not related to `ledgers` at all.

    Useful for queryset and reconciliation purposes.

    Relation is compulsory, but probably best defined at concrete class to
    be specific about subledger Relation, eg Creditor or Debtor.
    """

    bank_entry = models.OneToOneField(
        'bank_reconciliations.BankEntry',
        default='', blank=True, null=True)

    class Meta:
        abstract = True


class Relation(models.Model):

    # *** ABSTRACT CLASS ***

    """ All that `Relation` does is provide `get_relation` model method.
    """

    class Meta:
        abstract = True

    def clean_code(s):
        return s[:6]

    def get_or_create_relation(code, _Relation):
        """ `Entity` exists. `Creditor`/`Debtor` associated object) may not.

        We'll always want to just create related if `Entity` already exists.
        """
        try:
            return _Relation.objects.get(entity__code=code)
        except:
            try:
                # entity exists but creditor does not.
                # get entity, create creditor.
                entity = Entity.objects.get(code=code)
                if _Relation == Entity:
                    return entity
                return _Relation.objects.create(entity=entity)
            except Entity.DoesNotExist:
                raise Exception(
                    "Entity not found with code: {}".format(code))

    @classmethod
    def get_relation(cls, code, relation_class=None):
        """ get the correct related Entity for *this* whatever,
        eg `Creditor`/`Debtor`.

        Alternatively can specify using `object_name`

        Must be object instance eg. Creditor().get_relation("ACME")
        """

        code = Relation.clean_code(code)

        if relation_class:
            rel_cls = utils.get_source(relation_class)
        elif cls:
            rel_cls = utils.get_source(cls)

        return Relation.get_or_create_relation(code, import_string(rel_cls))

    def get_relation_by_entry(code, object_name):
        """ Specify the 'object_name' of the this you want the Relation of
        eg. object_name = 'CreditorInvoice', object_name = 'CreditorPayment'.

        Doesn't need to be instance.
        """
        object_settings = settings.OBJECT_SETTINGS[object_name]
        _Relation = import_string(object_settings.get('relation_class'))
        return Relation.get_or_create_relation(
            Relation.clean_code(code), _Relation)
