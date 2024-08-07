import re

from rest_framework import serializers


def validate_password(value):
    # password contains least one symbol lower case, one symbol upper case, one non-word symbol.
    # And length of password more, than 8
    pattern = re.compile(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?\W).{8,}$')
    if not pattern.match(value):
        raise serializers.ValidationError("Password is too week")
    return value
