import pygame


class Logger():
    LOG_EVENT: int = pygame.event.custom_type()
    IDX: int = 0

    @staticmethod
    def log(s: str, andprint: bool = True):
        if andprint:
            print(s)
        pygame.event.post(pygame.Event(Logger.LOG_EVENT, {'s': s, 'idx': Logger.IDX}))
        Logger.IDX += 1