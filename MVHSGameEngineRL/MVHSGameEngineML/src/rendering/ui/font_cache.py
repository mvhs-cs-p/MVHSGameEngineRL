import pygame


class FontCache:

    # static
    _cache = {}

    @classmethod
    def get(cls, font_name, size, name=None, bold=False, italic=False):
        key = (font_name, size, name, bold, italic)
        if key not in cls._cache:
            if font_name is None or font_name == "":
                cls._cache[key] = pygame.font.Font(None, size)
            else:
                cls._cache[key] = pygame.font.SysFont(font_name, size, bold=bold, italic=italic)

        return cls._cache[key]

