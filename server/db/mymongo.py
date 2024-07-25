from pymongo import MongoClient
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import hashlib


class MongoDBWrapper:
    """
    A wrapper class for interacting with MongoDB.

    用于与 MongoDB 进行交互的包装类。
    """

    def __init__(self, host, port, database):
        """
        Initializes a MongoDBWrapper instance.
        初始化 MongoDBWrapper 实例。
        Args:
            host (str): The MongoDB server host.
                MongoDB 服务器主机。
            port (int): The MongoDB server port.
                MongoDB 服务器端口。
            database (str): The name of the database to connect to.
                要连接的数据库的名称。
        """
        self.client = MongoClient(host, port)
        self.db = self.client[database]

    def insert_document(self, collection, document):
        """
        Inserts a document into the specified collection.
        将文档插入到指定的集合中。
        Args:
            collection (str): The name of the collection.
                集合的名称。
            document (dict): The document to be inserted.
                要插入的文档。
        """
        self.db[collection].insert_one(document)

    def find_documents(self, collection, query):
        """
        Finds documents in the specified collection based on the given query.
        根据给定的查询条件在指定的集合中查找文档。
        Args:
            collection (str): The name of the collection.
                集合的名称。
            query (dict): The query to filter the documents.
                用于筛选文档的查询条件。
        Returns:
            pymongo.cursor.Cursor: A cursor object containing the matching documents.
                包含匹配文档的游标对象。
        """
        return self.db[collection].find(query)

    def update_document(self, collection, query, update):
        """
        Updates a document in the specified collection based on the given query and update.

        根据给定的查询条件和更新内容在指定的集合中更新文档。

        Args:
            collection (str): The name of the collection.
                集合的名称。
            query (dict): The query to filter the documents.
                用于筛选文档的查询条件。
            update (dict): The update to be applied to the matching documents.
                要应用于匹配文档的更新内容。
        """
        self.db[collection].update_one(query, update)

    def delete_document(self, collection, query):
        """
        Deletes a document from the specified collection based on the given query.
        根据给定的查询条件从指定的集合中删除文档。
        Args:
            collection (str): The name of the collection.
                集合的名称。
            query (dict): The query to filter the documents.
                用于筛选文档的查询条件。
        """
        self.db[collection].delete_one(query)


# 示例使用
# 假设你已经有了一个私钥的PEM格式字符串
private_key_pem = """-----BEGIN RSA PRIVATE KEY-----
Zhangqiaoqing2024.
-----END RSA PRIVATE KEY-----"""


def encrypt_with_private_key_pem(input_string, key):
    # 创建一个sha256哈希对象
    hash_object = hashlib.sha256()

    # 将key和input_string合并，然后编码为字节串
    to_encrypt = (key + input_string).encode()

    # 给哈希对象提供数据
    hash_object.update(to_encrypt)

    # 获取十六进制格式的哈希值
    hashed = hash_object.hexdigest()

    return hashed


# # 示例使用
# # 假设你已经有了一个PEM格式的私钥字符串
# private_key_pem = """-----BEGIN PRIVATE KEY-----
# ...
# -----END PRIVATE KEY-----"""

# # 要加密的明文
# plaintext = "Hello, World!"

# # 加密数据
# encrypted_data = encrypt_with_private_key_pem(private_key_pem, plaintext)

# # 打印加密后的数据
# print("Encrypted Data:", encrypted_data)


# Example usage
if __name__ == "__main__":
    isc = encrypt_with_private_key_pem(
        "8851bb969c574e7c9e070d49598e3539", "Zhangqiaoqing2024."
    )
    print(isc)
    # b9084ed2202928a38b0626a98f217694aa3a8a12fd1c76994cef344e2d782fb3
    # Create an instance of the wrapper class
    # wrapper = MongoDBWrapper("localhost", 27017, "pubg_db")

    # # Insert a document
    # document = {"name": "John", "age": 30}
    # wrapper.insert_document("mycollection", document)

    # # Find documents
    # query = {"age": {"$gt": 25}}
    # results = wrapper.find_documents("mycollection", query)
    # for result in results:
    #     print(result)

    # # Update a document
    # query = {"name": "John"}
    # update = {"$set": {"age": 35}}
    # wrapper.update_document("mycollection", query, update)

    # Delete a document
    # query = {"name": "John"}
    # wrapper.delete_document("mycollection", query)
