from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Literal, Optional, Sequence

from bson import ObjectId
from motor.core import AgnosticCollection
from msgspec import convert, to_builtins
from pymongo import IndexModel
from typing_extensions import Self

from sshared.struct_constraints import ValidatableSturct

from .meta import Index

DocumentType = Dict[str, Any]
SortType = Dict[str, Literal["ASC", "DESC"]]


MODEL_META = {
    "frozen": True,
    "eq": False,
    "kw_only": True,
    "rename": "camel",
}


class Field(ValidatableSturct, **MODEL_META):
    def validate(self) -> Self:
        return convert(
            to_builtins(self, builtin_types=(ObjectId, datetime)),
            type=self.__class__,
        )


class Document(ValidatableSturct, **MODEL_META):
    class Meta:
        collection: AgnosticCollection
        indexes: Sequence[Index]

    @classmethod
    def _process_dict(cls, data: DocumentType) -> DocumentType:
        result: DocumentType = {}
        for key, value in data.items():
            if isinstance(value, dict):
                value = cls._process_dict(value)
            if isinstance(value, Enum):
                value = value.value

            result[key] = value

        return result

    @classmethod
    def _sort(cls, sort: SortType, /) -> Dict[str, int]:
        return {key: 1 if order == "ASC" else -1 for key, order in sort.items()}

    def validate(self) -> Self:
        return convert(
            to_builtins(self, builtin_types=(ObjectId, datetime)),
            type=self.__class__,
        )

    @classmethod
    def get_collection(cls) -> AgnosticCollection:
        return cls.Meta.collection

    @property
    def collection(self) -> AgnosticCollection:
        return self.Meta.collection

    @classmethod
    async def ensure_indexes(cls) -> None:
        index_models: List[IndexModel] = []

        for index in cls.Meta.indexes:
            if index.expire_after_seconds:
                index_models.append(
                    IndexModel(
                        keys=index.keys,
                        name=index.name,
                        unique=index.unique,
                        expireAfterSeconds=index.expire_after_seconds,
                    )
                )
            else:
                index_models.append(
                    IndexModel(
                        keys=index.keys,
                        name=index.name,
                        unique=index.unique,
                    )
                )

        await cls.Meta.collection.create_indexes(index_models)

    @classmethod
    def from_dict(cls, data: DocumentType, /) -> Self:
        return convert(data, type=cls)

    def to_dict(self) -> DocumentType:
        return to_builtins(self, builtin_types=(ObjectId, datetime))

    async def save(self) -> None:
        await self.__class__.insert_one(self)

    @classmethod
    async def find_one(
        cls,
        filter: Optional[DocumentType] = None,  # noqa: A002
        /,
        *,
        sort: Optional[SortType] = None,
    ) -> Optional[Self]:
        cursor = cls.Meta.collection.find(
            cls._process_dict(filter) if filter else {}
        ).limit(1)
        if sort:
            cursor = cursor.sort(cls._sort(sort))

        try:
            return cls.from_dict(await cursor.__anext__())
        except StopAsyncIteration:
            return None

    @classmethod
    async def find_many(
        cls,
        filter: Optional[DocumentType] = None,  # noqa: A002
        /,
        *,
        sort: Optional[SortType] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> AsyncGenerator[Self, None]:
        cursor = cls.Meta.collection.find(cls._process_dict(filter) if filter else {})
        if sort:
            cursor = cursor.sort(cls._sort(sort))
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)

        async for item in cursor:
            yield cls.from_dict(item)

    @classmethod
    async def insert_one(cls, data: Self, /) -> None:
        await cls.Meta.collection.insert_one(data.to_dict())

    @classmethod
    async def insert_many(cls, data: Sequence[Self], /) -> None:
        await cls.Meta.collection.insert_many(x.to_dict() for x in data)

    @classmethod
    async def count(
        cls,
        filter: Optional[DocumentType] = None,  # noqa: A002
        /,
        *,
        fast: bool = False,
    ) -> int:
        if fast:
            if filter:
                raise ValueError("文档数量估计值只能在无筛选条件时使用")

            return await cls.Meta.collection.estimated_document_count()

        return await cls.Meta.collection.count_documents(
            cls._process_dict(filter) if filter else {}
        )

    @classmethod
    async def update_one(cls, filter: DocumentType, update: DocumentType, /) -> None:  # noqa: A002
        await cls.Meta.collection.update_one(
            cls._process_dict(filter), cls._process_dict(update)
        )

    @classmethod
    async def update_many(cls, filter: DocumentType, update: DocumentType, /) -> None:  # noqa: A002
        await cls.Meta.collection.update_many(
            cls._process_dict(filter), cls._process_dict(update)
        )

    @classmethod
    async def delete_one(cls, filter: DocumentType, /) -> None:  # noqa: A002
        await cls.Meta.collection.delete_one(cls._process_dict(filter))

    @classmethod
    async def delete_many(cls, filter: DocumentType, /) -> None:  # noqa: A002
        await cls.Meta.collection.delete_many(cls._process_dict(filter))

    @classmethod
    async def aggregate_one(
        cls, pipeline: Sequence[DocumentType]
    ) -> Optional[DocumentType]:
        try:
            await cls.Meta.collection.aggregate(pipeline).__anext__()  # type: ignore
        except StopAsyncIteration:
            return None

    @classmethod
    async def aggregate_many(
        cls, pipeline: Sequence[DocumentType]
    ) -> AsyncGenerator[DocumentType, None]:
        async for item in cls.Meta.collection.aggregate(pipeline):  # type: ignore
            yield item
