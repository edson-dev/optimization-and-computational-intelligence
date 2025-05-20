from dataset.util import ResultIter
import  dataset


class RepositorySQL:
    def __init__(self, address: str = "sqlite:///:memory:", schema: str = None):
        self.address = address
        self.schema = schema
        self.db: dataset.Database = dataset.connect(self.address, self.schema, sqlite_wal_mode=False)


    def __enter__(self):
        return self

    def __exit__(self, typ, val, traceback):
        ...

    def upsert(self, table: str, data: dict, keys: list[str] = None) -> dict:
        if not keys:
            keys = ["id"]
        res = self.db[table].upsert(data, keys=keys, ensure=True, types={"id": self.db.types.json})
        r: ResultIter = self.db[table].find(**data)
        return  r if r else {}

    def search(self, table: str, query: dict, limit: int = 10, skip: int = 0) -> list[dict]:
        limit: int = query.pop("limit", limit)
        skip: int = query.pop("skip", skip)
        key = None
        if table not in self.db.tables:
            return None
        t: dataset.Table = self.db[table]
        results: ResultIter = t.find(**query, _limit=limit, _offset=skip, order_by=[key])
        return list(results)

