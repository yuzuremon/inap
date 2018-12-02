import requests
import json
import os

class SlackClient():
    def __init__(self):
        # slack投稿用URL
        self.web_hook_url = 'https://slack.com/api/chat.postMessage'
        # 環境変数から投稿するチャンネルとAPIトークンを取得
        self.channel = os.environ.get('SLACK_CHANNEL')
        self.token = os.environ.get('SLACK_TOKEN')
        # slack送信用のHeader
        self.headers = {
            'Content-Type' : 'application/json; charset=utf-8',
            'Authorization' : 'Bearer {}'.format(self.token)
        }
        # Slack送信用データを作成
        self.data = {'channel': self.channel}

    def send(self, attachments, thread_ts=None):
        """Slackへ送信を行う"""
        self.data['attachments'] = attachments
        if thread_ts is not None:
            self.data['thread_ts'] = thread_ts
        return requests.post(self.web_hook_url, data = json.dumps(self.data), headers = self.headers)
