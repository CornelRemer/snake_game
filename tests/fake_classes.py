from typing import List

from snake.publisher import AbstractPublisher, AbstractSubscriber, PublisherEvents


class FakePublisher(AbstractPublisher):
    def __init__(self):
        self._subscribers: List[AbstractSubscriber] = []
        self._published_events: List[PublisherEvents] = []

    def add_subscriber(self, subscriber: AbstractSubscriber) -> None:
        self._subscribers.append(subscriber)

    def publish_one_event(self, event: PublisherEvents) -> None:
        self._published_events.append(event)

    @property
    def all_events(self) -> List[PublisherEvents]:
        return self._published_events

    @property
    def subscribers(self) -> List[AbstractSubscriber]:
        return self._subscribers


class FakeSubscriber(AbstractSubscriber):
    def __init__(self):
        self._received_events: List[PublisherEvents] = []

    def get_notified(self, event: PublisherEvents) -> None:
        self._received_events.append(event)

    @property
    def received_notifications(self) -> List[PublisherEvents]:
        return self._received_events
