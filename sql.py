from typing import Optional

from dataset.util import ResultIter

import  dataset


class RepositorySQL:
    def __init__(self, address: str = "sqlite:///:memory:", schema: str = None):
        self.address = address
        self.schema = schema
        self.db: dataset.Database = dataset.connect(self.address, self.schema, sqlite_wal_mode=False)


    def __enter__(self):
        if self.db is None:
            try:
                self.db: dataset.Database = dataset.connect(self.address, self.schema)
            finally:
                self.db.close()
        return self

    def __exit__(self, typ, val, traceback):
        ...

    def describe(self) -> list[dict]:
        r = [{"table": table, "size": self.db[table].count(), "columns": self.db[table].columns} for table in self.db.tables]
        return r

    def search(self, table: str, query: dict, limit: int = 10, skip: int = 0) -> Optional[list[dict]]:
        limit: int = query.pop("limit", limit)
        skip: int = query.pop("skip", skip)
        key = None
        if table not in self.db.tables:
            return None
        for k in list(query.keys()):
            if k not in self.db[table].columns:
                del query[k]
        results: ResultIter = self.db[table].find(**query, _limit=limit, _offset=skip, order_by=[key])
        result = list(results)
        # TODO refactor to remove _ protect stats
        for i in result:
            for k in i:
                if k.startswith("_"):
                    i.pop(k)
        return list(result)

    def delete(self, table: str, query: dict) -> bool:
        if table not in self.db.tables:
            return False
        d = self.db[table].delete(**query)
        return d

    def insert(self, table: str, data: dict) -> dict:
        r = self.db[table].insert(data)
        return {"id": r} | data if r else {}

    def upsert(self, table: str, data: dict, keys: list[str] = None) -> dict:
        if not keys:
            keys = ["id"]
        res = self.db[table].upsert(data, keys=keys, ensure=True, types={"id": self.db.types.json})
        r: ResultIter = self.db[table].find(**data)
        filtdict = {k: v for k, v in list(r)[0].items() if not k.startswith('_')}
        return  filtdict if res else {}

    def execute(self, query: str) -> list:
        r: ResultIter = self.db.query(query)
        return list(r) if r else {}
