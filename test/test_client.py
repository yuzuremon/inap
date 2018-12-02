from redisclient import RedisClient

class TestRedisClient():
    def setup_method(self):
        self.redis = RedisClient()

    def teardown_method(self):
        pass

    def test_add(self):
        self.redis.add('test_key', 'https://www.google.co.jp/', '1999-01-01 00:00:00')
        test_keys = self.redis.get('test_key')
        assert 'https://www.google.co.jp/' == test_keys[b'url'].decode()
        assert '1999-01-01 00:00:00' == test_keys[b'previous_time'].decode()
        self.redis.delete('test_key')

    def test_update_previous_time(self):
        self.redis.add('test_key', 'https://www.google.co.jp/', '1999-01-01 00:00:00')
        self.redis.update_previous_time('test_key', '2000-12-31 00:00:00')
        test_keys = self.redis.get('test_key')
        assert '2000-12-31 00:00:00' == test_keys[b'previous_time'].decode()
        self.redis.delete('test_key')
