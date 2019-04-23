import re

SMS_CHAR_COUNT_LIMIT = 612  # 153 * 4

# regexes for use in recipients.validate_email_address.
# Valid characters taken from https://en.wikipedia.org/wiki/Email_address#Local-part
# Note: Normal apostrophe eg `Firstname-o'surname@domain.com` is allowed.
hostname_part = re.compile(r'^(xn-|[a-z0-9]+)(-[a-z0-9]+)*$', re.IGNORECASE)
tld_part = re.compile(r'^([a-z]{2,63}|xn--([a-z0-9]+-)*[a-z0-9]+)$', re.IGNORECASE)
VALID_LOCAL_CHARS = r"a-zA-Z0-9.!#$%&'*+/=?^_`{|}~\-"
EMAIL_REGEX_PATTERN = r'^[{}]+@([^.@][^@\s]+)$'.format(VALID_LOCAL_CHARS)
email_with_smart_quotes_regex = re.compile(
    # matches wider than an email - everything between an at sign and the nearest whitespace
    r'(^|\s)\S+@\S+(\s|$)',
    flags=re.MULTILINE,
)
