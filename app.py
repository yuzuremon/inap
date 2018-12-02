import feedparser
import falcon
import json
import re
import urllib
from dateutil.parser import parse
from redisclient import RedisClient
from slackclient import SlackClient

class AppResource():
    def __init__(self):
        # RedisClient
        self.redis = RedisClient()

    def on_get(self, req, res):
        """登録したRSSを読み取ってSlackへ新着記事を送信する"""
        slackclient = SlackClient()

        # 登録されたRSS数分処理を行う
        for key in self.redis.get_key_all():
            # RSSのURL、最後に取得した記事の作成日時を取得
            rss_config_dict = self.redis.get(key)
            url = rss_config_dict[b'url'].decode()
            # RSS読み取り
            rss = feedparser.parse(url)

            # パースが成功している場合のみ処理を行う
            if rss.bozo == 0:
                # 最後に取得した記事の作成日時より新しい記事のみ取得
                last_items = -1
                previous_time = self.time_format(rss_config_dict[b'previous_time'].decode())
                for entry in rss.entries:
                    if previous_time < self.time_format(entry.published):
                        last_items += 1
                    else:
                        break

                # 新着記事が存在する場合のみSlackへ通知を送信
                if last_items > -1:
                    # Slackへ送信するattachmentsを作成
                    attachments = self.create_attachments(rss, last_items, key)
                    # スレッドタイトルを送信
                    res = slackclient.send([{'title': '新着通知：{}'.format(rss.entries.title)}])
                    # スレッドのタイトルに紐付けて新着記事を送信
                    slackclient.send(attachments, thread_ts=res.json()['ts'])
            else:
                # パースに失敗した場合はエラーを出力して処理続行
                print('title: {}, url: {}, error: {}'.format(key, url, rss.bozo_exception))

        res.body = 'OK'

    def on_post(self, req, res):
        """
        RSSの一覧表示、新規登録、削除を行う
        リクエストのコマンドで分岐
        showrss：一覧表示
        addrss：登録
        delrss：削除
        """
        # postパラメーターを取得
        params = urllib.parse.parse_qs(req.stream.read())
        command = params[b'command'][0].decode()
        msg = ''
        if '/showrss' == command:
            # RSSの一覧を表示
            msg = 'RSSList : \n - ' + '\n - '.join([key.decode() for key in self.redis.get_key_all()])
        elif '/addrss' == command:
            # RSS登録を実施
            url = params[b'text'][0].decode()
            # URL形式チェック
            if re.match(r'^https?:\/\/', url):
                rss = feedparser.parse(url)
                # パースが成功している場合のみ処理を行う
                if rss.bozo == 0:
                    title = rss.feed.title
                    self.redis.add(title, url, self.time_format(rss.entries[1].published))
                    msg = 'RSS登録完了: {}'.format(title)
                else:
                    # パースに失敗した場合はエラーを出力して処理続行
                    print('url: {}, error: {}'.format(url, rss.bozo_exception))
                    msg = 'URLが存在しないか、またはRSSとして読み取り出来ませんでした。'
            else:
                msg = 'URLは http://、https:// から記述してください。'
        elif '/delrss' == command:
            # RSS削除を実施
            title = params[b'text'][0].decode()
            self.redis.delete(title)
            msg = 'RSS削除完了: {}'.format(title)

        res.body = msg

    def create_attachments(self, rss, last_items, key):
        """取得した記事からattachmentsを生成"""
        attachments = []
        for i in range(last_items, -1, -1):
            # 取得した記事の作成日時を保存
            published = rss.entries[i].published
            self.redis.update_previous_time(key, self.time_format(published))

            summary = rss.entries[i].summary
            # 投稿した記事をattachmentに追加
            attachments.append(
                {
                    'title' : '<{}|{}>'.format(rss.entries[i].link, rss.entries[i].title),  # タイトルと記事のリンク
                    'text' : re.compile(r'<[^>]*?>').sub('', summary) if summary is not None else '',  # 記事のサマリー
                    'footer' : self.time_format(published)  # 記事の投稿時間
                }
            )
        return attachments

    def time_format(self, time):
        """引数で渡されたtimeを[YYYY-MM-DD HH:MM:SS]フォーマットで返却"""
        return parse(time).strftime('%Y-%m-%d %H:%M:%S')

app = falcon.API()
app.add_route("/", AppResource())

if __name__ == '__main__':
    from wsgiref import simple_server
    httpd = simple_server.make_server("127.0.0.1", 8000, app)
    httpd.serve_forever()
