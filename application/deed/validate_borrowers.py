"""
Checks the validity of the borrowers.

According to the following business rules:

- All registered proprietors must be named as borrowers on the mortgage deed.
- Conveyancer must be alerted if the registered proprietors and mortgage deed borrower names do not match.
- Names do not need to be in the same order that they are on the register.
- Names must not be case sensitive.
"""

import collections

import itertools

from application.register_adapter.service import RegisterAdapter
from flask import current_app


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
    lowercase_names = [x.lower() for x in names]
    return set(itertools.chain(*[["{0}.{1}".format(j, i)
                                  for i, j in enumerate(y * [x])]
                                 for x, y in
                                 collections.Counter(lowercase_names).items()]))


def _unmatched_names(proprietor_names, deed_names):
    """
    Testing equality of names from two sources.

    :param proprietor_names: The names on the Register.
    :type proprietor_names: list
    :param deed_names: The names on the Deed.
    :type deed_names: list
    :returns: The names that are not on the Register but on the Deed.
    :rtype: set
    """
    register_set = _set_no_duplicates(proprietor_names)
    deed_set = _set_no_duplicates(deed_names)
    return register_set.symmetric_difference(deed_set)


class BorrowerNamesDifferException(Exception):
    pass


class BorrowerNamesMissingException(Exception):
    pass


def compare_borrower_names(payload):
    """
    Check that the names on the payload are valid.
    """
    deed_names = _unpack_borrowers(payload)
    title_number = payload.get('title_number')
    proprietor_names = RegisterAdapter.get_proprietor_names(title_number)
    unmatched_names = _unmatched_names(proprietor_names, deed_names)
    if unmatched_names:
        current_app.logger.info(
            "%s Names on Register and deed do not match for title number '%s'" % (len(unmatched_names), title_number))
        raise BorrowerNamesDifferException


def all_borrower_names_present(payload):
    """
    Check that the enough Borrower names exist in the payload.
    """
    deed_names = _unpack_borrowers(payload)
    title_number = payload.get('title_number')
    proprietor_names = RegisterAdapter.get_proprietor_names(title_number)
    missing_borrower_name_count = len(proprietor_names) - len(deed_names)
    if missing_borrower_name_count > 0:
        current_app.logger.info(
            "%s Borrower names missing for title number '%s'" % (missing_borrower_name_count, title_number))
        raise BorrowerNamesMissingException
