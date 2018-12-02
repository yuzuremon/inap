import pytest
import feedparser
import re
from dateutil.parser import parse
from app import AppResource
from redisclient import RedisClient

class TestAppResource():
    def setup_method(self):
        self.app = AppResource()

    def teardown_method(self):
        pass

    def test_create_attachments(self, monkeypatch):
        rss = feedparser.parse('https://qiita.com/tags/python/feed')
        def update_previous_time_dummy(self, key, previous_time):
            assert key == 'key'
            assert previous_time == parse(rss.entries[0].published).strftime('%Y-%m-%d %H:%M:%S')

        monkeypatch.setattr(RedisClient, 'update_previous_time', update_previous_time_dummy)
        attachments = self.app.create_attachments(rss, 0, 'key')
        assert attachments[0]['title'] == '<{}|{}>'.format(rss.entries[0].link, rss.entries[0].title)
        assert attachments[0]['text'] == re.compile(r'<[^>]*?>').sub('', rss.entries[0].summary) if summary is not None else ''
        assert attachments[0]['footer'] == parse(rss.entries[0].published).strftime('%Y-%m-%d %H:%M:%S')

    @pytest.mark.parametrize('time, answer', [
        ('2000-01-01T00:00:00+00:00', '2000-01-01 00:00:00'),
        ('2018-11-30T18:00:04.071+09:00', '2018-11-30 18:00:04'),
        ('2018-11-30T07:51:59Z', '2018-11-30 07:51:59'),
        ('Fri, 30 Nov 2018 20:05:40 +0000', '2018-11-30 20:05:40'),
    ])
    def test_time_format(self, time, answer):
        assert answer == self.app.time_format(time)
