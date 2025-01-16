import plyvel
import os
import fasteners
import pickle


class LevelDB:
    _db_path = "/opt/.data/rbk/private/runtimes/containers_leveldb"
    _lock_file_path = os.path.join('/tmp', 'containers_leveldb.lock')  # 分离锁文件路径
    _db = None
    _lock = fasteners.InterProcessLock(_lock_file_path)

    @staticmethod
    def _to_bytes(data):
        if isinstance(data, bytes):
            return data
        else:
            return pickle.dumps(data)

    @staticmethod
    def _from_bytes(data):
        try:
            return pickle.loads(data)
        except pickle.UnpicklingError:
            return data.decode('utf-8')

    @classmethod
    def init_db(cls):
        if cls._db is None:
            with cls._lock:  # 确保初始化时只有一个进程创建数据库
                if cls._db is None:  # 双重检查lock
                    try:
                        cls._db = plyvel.DB(cls._db_path, create_if_missing=True)
                    except Exception as e:
                        print(f"LevelDB: Failed to initialize database: {e}")
                        return False
        return True

    @classmethod
    def put(cls, key: str, value):
        cls.init_db()
        with cls._lock:  # 写锁
            try:
                cls._db.put(cls._to_bytes(key), cls._to_bytes(value))
                print(f"LevelDB: Data put successfully: {key} -> {value}")
                return True
            except Exception as e:
                print(f"LevelDB: Failed to put data into database: {e}")
                return False

    @classmethod
    def get(cls, key: str):
        cls.init_db()
        try:
            result = cls._db.get(cls._to_bytes(key))
            if result is None:
                print(f"LevelDB: Key not found: {key}")
                return None
            return cls._from_bytes(result)  # 返回原始数据类型
        except Exception as e:
            print(f"LevelDB: Failed to get data from database: {e}")
            return None

    @classmethod
    def delete(cls, key: str):
        cls.init_db()
        with cls._lock:  # 写锁
            try:
                cls._db.delete(cls._to_bytes(key))
                print(f"LevelDB: Data deleted successfully: {key}")
                return True
            except Exception as e:
                print(f"LevelDB: Failed to delete data from database: {e}")
                return False

    @classmethod
    def close_db(cls):
        if cls._db is not None:
            cls._db.close()
            cls._db = None
            print("LevelDB: Database connection closed successfully")
            return True
        print("LevelDB: Database connection was already closed")
        return True


# 示例使用方法
if __name__ == '__main__':
    LevelDB.put('key1', 'value1')
    LevelDB.put('key2', 123)
    LevelDB.put('key3', {'name': 'value3'})
    print("db.get('key1'):", LevelDB.get('key1'))
    print("db.get('key2'):", LevelDB.get('key2'))
    result = LevelDB.get('key3')
    print("type(db.get('key3')):", type(result))
    print("db.get('key3'):", result)

    LevelDB.delete('key1')
    print("db.get('key1'):", LevelDB.get('key1'))