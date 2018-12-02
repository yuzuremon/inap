import redis
import os

class RedisClient():
    def __init__(self):
        """Redisに接続"""
        # 環境変数からURLを取得
        pool = redis.ConnectionPool.from_url(os.environ.get('REDIS_URL'), 0)
        self.r = redis.StrictRedis(connection_pool=pool)

    def get(self, key):
        """key単位で設定情報を取得"""
        return self.r.hgetall(key)

    def get_key_all(self):
        """設定されているkeyを全て取得"""
        return self.r.keys()

    def add(self, key, url, previous_time):
        """新規RSSの登録"""
        self.r.hmset(key, {'url': url, 'previous_time': previous_time})

    def update_previous_time(self, key, previous_time):
        """previous_timeの更新を行う"""
        self.r.hset(key, 'previous_time', previous_time)

    def delete(self, key):
        """登録RSSの削除を行う"""
        self.r.delete(key)
