import pygame
from MVHSGameEngineML.src.utilities import Logger

class ImageCache:

    # static
    _cache = {}


    @classmethod
    def load_image_scaled(cls, image_path, width_scale, height_scale):
        key = (image_path, width_scale, height_scale)
        if key not in cls._cache:

            try:
                surface = pygame.image.load(str(image_path)).convert_alpha()
                if width_scale == 1 and height_scale == 1:
                    cls._cache[key] = surface
                else:
                    width, height = surface.get_size()
                    new_scale = int(round(width * width_scale)), int(round(height * height_scale))
                    surface = pygame.transform.smoothscale(surface, new_scale)
                    cls._cache[key] = surface
            except (pygame.error, FileNotFoundError, OSError) as e:
                Logger.log_error(cls, f"Unable to load {image_path}. Error {e}")
                surface = pygame.Surface((100, 100))
                surface.fill((255, 0, 255))
                cls._cache[key] = surface

        return cls._cache[key]

    @classmethod
    def load_image(cls, image_path, default_scale:float = 1):
        key = (image_path, default_scale, default_scale)
        if key not in cls._cache:

            try:
                surface = pygame.image.load(str(image_path)).convert_alpha()
                if default_scale == 1:
                    cls._cache[key] = surface
                else:
                    width, height = surface.get_size()
                    new_scale = int(round(width * default_scale)), int(round(height * default_scale))
                    surface = pygame.transform.smoothscale(surface, new_scale)
                    cls._cache[key] = surface
            except (pygame.error, FileNotFoundError, OSError) as e:
                Logger.log_error(cls, f"Unable to load {image_path}. Error {e}")
                surface = pygame.Surface((100, 100))
                surface.fill((255, 0, 255))
                cls._cache[key] = surface

        return cls._cache[key]