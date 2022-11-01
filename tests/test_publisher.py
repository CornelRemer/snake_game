from typing import Dict

import pytest

from snake.publisher import Publisher, PublisherEvents, ScoreSubscriber
from tests.fake_classes import FakeSubscriber


class TestPublisher:
    def test_add_subscriber(self, fake_subscriber: FakeSubscriber):
        publisher = Publisher()
        publisher.add_subscriber(fake_subscriber)

        assert publisher.subscribers == [fake_subscriber]

    def test_publish_one_event(self, fake_subscriber: FakeSubscriber):
        publisher = Publisher()
        publisher.add_subscriber(fake_subscriber)

        event = PublisherEvents.COLLISION_DETECTED
        publisher.publish_one_event(event)

        assert fake_subscriber.received_notifications == [PublisherEvents.COLLISION_DETECTED]


class TestScoreSubscriber:
    @pytest.mark.parametrize(
        "event, expected_state",
        ((PublisherEvents.REACHED_FOOD, {"score": 1}), (PublisherEvents.COLLISION_DETECTED, {"score": 0})),
    )
    def test_got_notified_handles_events_correctly(self, event: PublisherEvents, expected_state: Dict[str, int]):
        state = {"score": 0}
        subscriber = ScoreSubscriber(state)

        subscriber.get_notified(event)
        assert state == expected_state
