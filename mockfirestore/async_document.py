from copy import deepcopy
from typing import Dict, Any
from mockfirestore import NotFound
from mockfirestore._helpers import flatten_for_merge
from mockfirestore.document import DocumentReference, DocumentSnapshot


class AsyncDocumentReference(DocumentReference):
    async def get(self) -> DocumentSnapshot:
        return super().get()

    async def delete(self):
        super().delete()

    async def set(self, data: Dict[str, Any], merge=False):
        # Mirrors the sync set's merge branch with awaits: the sync
        # implementation calls self.update, which dispatches to the async
        # override here and would return an unawaited coroutine.
        if merge:
            data = deepcopy(data)
            data['__name__'] = self.id
            try:
                await self.update(flatten_for_merge(data))
            except NotFound:
                super().set(data, merge=False)
        else:
            super().set(data, merge=False)

    async def update(self, data: Dict[str, Any]):
        super().update(data)

    def collection(self, name) -> 'AsyncCollectionReference':
        from mockfirestore.async_collection import AsyncCollectionReference
        coll_ref = super().collection(name)
        return AsyncCollectionReference(coll_ref._data, coll_ref._path, self)
