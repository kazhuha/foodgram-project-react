from django.core.exceptions import ValidationError
from webcolors import CSS3_NAMES_TO_HEX


def validate_hex_color(value: str) -> bool:
    """Проверяет сущестует ли такой цвет в
    HEX библиотеке"""
    if value not in CSS3_NAMES_TO_HEX:
        raise ValidationError(
            'Такого цвета не существует',
            params={'value': value}
        )
