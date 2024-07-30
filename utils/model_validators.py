from django.core.exceptions import ValidationError


def validate_png(image):
    if not image.name.lower().endswith('.bmp'):
        raise ValidationError('Imagem bmp')
