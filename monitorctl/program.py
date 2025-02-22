from abc import ABC


class Program(ABC):
    @abstractmethod
    def update(items: List | Dict):
        pass

    @abstractmethod
    def config() -> Iterable:
        return None
