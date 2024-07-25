import redis


class RedisWrapper:
    def __init__(self, host="localhost", port=6379, db=0):
        """
        初始化RedisWrapper对象。

        Args:
            host (str, optional): Redis服务器的主机名。默认为"localhost"。
            port (int, optional): Redis服务器的端口号。默认为6379。
            db (int, optional): Redis数据库的索引。默认为0。
        """
        self.redis_client = redis.Redis(host=host, port=port, db=db, ssl=False)

    def set(self, key, value):
        """
        将指定的键值对存储到Redis中。

        Args:
            key (str): 要存储的键。
            value (str): 要存储的值。
        """
        self.redis_client.set(key, value)

    def get(self, key):
        """
        从Redis中获取指定键的值。

        Args:
            key (str): 要获取值的键。

        Returns:
            str: 指定键的值，如果键不存在则返回None。
        """
        return self.redis_client.get(key)

    def delete(self, key):
        """
        从Redis中删除指定的键值对。

        Args:
            key (str): 要删除的键。
        """
        self.redis_client.delete(key)

    def update(self, key, value):
        """
        更新Redis中指定键的值。

        如果键存在，则更新其对应的值为指定的值；如果键不存在，则抛出KeyError异常。

        Args:
            key (str): 要更新的键。
            value (str): 新的值。

        Raises:
            KeyError: 如果指定的键在Redis中不存在。
        """
        if self.redis_client.exists(key):
            self.redis_client.set(key, value)
        else:
            raise KeyError(f"键 '{key}' 在Redis中不存在。")

    def flushall(self):
        """
        清空Redis中的所有键值对。
        """
        self.redis_client.flushdb()
