import requests
import json
import pytest
from slackclient import SlackClient

class TestSlackClient():
    def setup_method(self):
        self.slackclient = SlackClient()

    def teardown_method(self):
        pass

    @pytest.mark.parametrize('title, thread_ts', [
        ('test', None),
        ('test', 'thread_ts'),
    ])
    def test_send_slack_thread(self, monkeypatch, title, thread_ts):
        def requests_post_dummy(url, data, headers):
            dict = json.loads(data)
            assert url == 'https://slack.com/api/chat.postMessage'
            assert headers['Content-Type'] == 'application/json; charset=utf-8'
            assert dict['attachments']['title'] == 'test'
            if thread_ts is not None:
                assert dict['thread_ts'] == thread_ts
            return requests.Response

        monkeypatch.setattr(requests, 'post', requests_post_dummy)
        attachments = {}
        attachments['title'] = title
        if thread_ts is not None:
            self.slackclient.send(attachments, thread_ts=thread_ts)
        else:
            self.slackclient.send(attachments)
