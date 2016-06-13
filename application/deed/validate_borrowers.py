"""
Checks the validity of the borrowers.

According to the following business rules:

- Conveyancer must be alerted if more names are on the register than on the mortgage deed.
- All names on the register must be on the mortgage deed.
- There can be more names on the mortgage deed than on the register.
- Conveyancer does not need to be alerted that there are more names on mortgage deed than register.
- Names do not need to be in the same order that they are on the register.
- Names must not be case sensitive.
"""


import collections
import itertools
import logging


from application.register_adapter.service import RegisterAdapter


LOGGER = logging.getLogger(__name__)


def _unpack_borrowers(payload):
    """
    Extract the borrower names from json

    :type payload: dict
    :rtype: list
    """
    return [" ".join([name for name in [borrower.get('forename'),
                                        borrower.get('middle_name'),
                                        borrower.get('surname')] if name])
            for borrower in payload['borrowers']]


def _set_no_duplicates(names):
    """
    Cast to a `set` but first making the elements unique
    by adding a count suffix.

    :type names: list
    :rtype: set
    """
    return set(itertools.chain(*[["{0}.{1}".format(j, i)
                               for i, j in enumerate(y*[x.lower()])]
                               for x, y in
                                 collections.Counter(names).items()]))


def _complement_names(proprietor_names, deed_names):
    """
    The Relative Complement of names on the Deed.

    :param proprietor_names: The names on the Register.
    :type proprietor_names: list
    :param deed_names: The names on the Deed.
    :type deed_names: list
    :returns: The names that are not on the Register but on the Deed.
    :rtype: set
    """
    register_set = _set_no_duplicates(proprietor_names)
    deed_set = _set_no_duplicates(deed_names)
    return set([name for name in register_set if name not in deed_set])


class BorrowerNamesException(Exception):
    pass


def check_borrower_names(payload):
    """
    Check that the names on the payload are valid.
    """
    deed_names = _unpack_borrowers(payload)
    title_number = payload.get('title_number')
    proprietor_names = RegisterAdapter.get_proprietor_names(title_number)
    complement = _complement_names(proprietor_names, deed_names)
    if complement:
        names = ','.join(complement)
        LOGGER.info("Names on Register but not on Deed '%s'", names)
        raise BorrowerNamesException
