from typing import Dict

import pytest

from snake.publisher import (
    Publisher,
    PublisherEvents,
    RewardSubscriber,
    ScoreSubscriber,
)
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
        "event, expected_remuneration",
        ((PublisherEvents.REACHED_FOOD, {"score": 1}), (PublisherEvents.COLLISION_DETECTED, {"score": 0})),
    )
    def test_got_notified_handles_events_correctly(self, event: PublisherEvents, expected_remuneration: Dict[str, int]):
        remuneration = {"score": 0}
        subscriber = ScoreSubscriber(remuneration)

        subscriber.get_notified(event)
        assert remuneration == expected_remuneration


class TestRewardSubscriber:
    @pytest.mark.parametrize(
        "event, expected_remuneration",
        (
            (PublisherEvents.REACHED_FOOD, {"score": 1, "reward": 50}),
            (PublisherEvents.COLLISION_DETECTED, {"score": 0, "reward": -10}),
        ),
    )
    def test_got_notified_handles_events_correctly(self, event: PublisherEvents, expected_remuneration: Dict[str, int]):
        remuneration = {"score": 0, "reward": 0}
        subscriber = RewardSubscriber(remuneration)

        subscriber.get_notified(event)
        assert remuneration == expected_remuneration
