from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Callable, Dict, List


class PublisherEvents(Enum):
    COLLISION_DETECTED = auto()
    REACHED_FOOD = auto()


class AbstractSubscriber(ABC):
    @abstractmethod
    def get_notified(self, event: PublisherEvents) -> None:
        pass


class ScoreSubscriber(AbstractSubscriber):
    def __init__(self, state: Dict[str, int]):
        self._state = state

    def get_notified(self, event: PublisherEvents) -> None:
        if self._subscribed(event):
            handler = self._get_handler_for_event(event)
            handler()

    def _subscribed(self, event: PublisherEvents) -> bool:
        return event in self._subscribed_events

    @property
    def _subscribed_events(self) -> Dict[PublisherEvents, Callable]:
        return {
            PublisherEvents.REACHED_FOOD: self._increase_score,
        }

    def _increase_score(self) -> None:
        self._state["score"] += 1

    def _get_handler_for_event(self, event: PublisherEvents) -> Callable:
        return self._subscribed_events[event]


class AbstractPublisher(ABC):
    @abstractmethod
    def add_subscriber(self, subscriber: AbstractSubscriber) -> None:
        pass

    @abstractmethod
    def publish_one_event(self, event: PublisherEvents) -> None:
        pass


class Publisher(AbstractPublisher):
    def __init__(self):
        self._subscribers: List[AbstractSubscriber] = []

    def add_subscriber(self, subscriber: AbstractSubscriber):
        self._subscribers.append(subscriber)

    def publish_one_event(self, event: PublisherEvents) -> None:
        for subscriber in self._subscribers:
            subscriber.get_notified(event)

    @property
    def subscribers(self) -> List[AbstractSubscriber]:
        return self._subscribers