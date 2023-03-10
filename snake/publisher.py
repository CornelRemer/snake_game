from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Callable, Dict, List


class PublisherEvents(Enum):
    COLLISION_DETECTED = auto()
    REACHED_FOOD = auto()
    NO_COLLISION = auto()


class AbstractSubscriber(ABC):
    def get_notified(self, event: PublisherEvents) -> None:
        if self._subscribed(event):
            handler = self._get_handler_for_event(event)
            handler()

    def _subscribed(self, event: PublisherEvents) -> bool:
        return event in self._subscribed_events

    @property
    @abstractmethod
    def _subscribed_events(self) -> Dict[PublisherEvents, Callable]:
        pass

    def _get_handler_for_event(self, event: PublisherEvents) -> Callable:
        return self._subscribed_events[event]


class ScoreSubscriber(AbstractSubscriber):
    def __init__(self, remuneration: Dict[str, int]):
        self._remuneration = remuneration

    @property
    def _subscribed_events(self) -> Dict[PublisherEvents, Callable]:
        return {
            PublisherEvents.REACHED_FOOD: self._increase_remuneration,
        }

    def _increase_remuneration(self) -> None:
        self._remuneration["score"] += 1


class RewardSubscriber(AbstractSubscriber):
    def __init__(self, remuneration: Dict[str, int]):
        self._remuneration = remuneration

    @property
    def _subscribed_events(self) -> Dict[PublisherEvents, Callable]:
        return {
            PublisherEvents.REACHED_FOOD: self._increase_reward,
            PublisherEvents.COLLISION_DETECTED: self._decrease_reward,
        }

    def _increase_reward(self) -> None:
        self._remuneration["reward"] = 10

    def _decrease_reward(self) -> None:
        self._remuneration["reward"] = -10


class NoCollisionSubscriber(AbstractSubscriber):
    def __init__(self, remuneration: Dict[str, int]):
        self._remuneration = remuneration

    @property
    def _subscribed_events(self) -> Dict[PublisherEvents, Callable]:
        return {
            PublisherEvents.NO_COLLISION: self._reset_reward,
        }

    def _reset_reward(self) -> None:
        self._remuneration["reward"] = 0


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
