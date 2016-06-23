from underscore import _
import re

BASIC_POSTCODE_REGEX = '^[A-z]{1,2}[0-9R][0-9A-z]? ?[0-9][A-z]{2}$'
HOUSE_CODE = '^[0-9]{1,}[A-z]{0,1}$'
BASIC_POSTCODE_WITH_SURROUNDING_GROUPS_REGEX = (
    r'(?P<leading_text>.*\b)\s?'
    r'(?P<postcode>[A-z]{1,2}[0-9R][0-9A-z]? [0-9][A-z]{2}\b)\s?'
    r'(?P<trailing_text>.*)'
)


def format_address_string(address_string):

    def remove_whitespace(x, index, list):
        return x.strip()

    def uppercase_if_postcode(x, index, list):
        return x.upper() if re.search(BASIC_POSTCODE_REGEX, x.upper()) else x

    def handle_house_number(result, x, index):
        if index == 1 and re.search(HOUSE_CODE, result[0]):
            result = [result[0] + ' ' + x]
        else:
            result.append(x)
        return result

    def make_postcode_last(context, x, index):

        matches = re.match(BASIC_POSTCODE_WITH_SURROUNDING_GROUPS_REGEX, x)
        slots = len(context)
        if index > 1 and re.search(BASIC_POSTCODE_REGEX, context[slots-1]):
            postcode = context[slots-1]
            context[slots-1] = x
            context.append(postcode)
        elif matches:
            if matches.group('leading_text') and len(matches.group('leading_text').strip()) > 0:
                context.append(matches.group('leading_text').strip())
            if matches.group('trailing_text') and len(matches.group('trailing_text').strip()) > 0:
                context.append(matches.group('trailing_text').strip())
            context.append(matches.group('postcode').strip())
        else:
            context.append(x)
        return context

    return _(address_string.split(',')).chain()\
        .map(remove_whitespace)\
        .reduce(handle_house_number, [])\
        .reduce(make_postcode_last, [])\
        .map(uppercase_if_postcode)\
        .value()
