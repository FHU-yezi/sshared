from datetime import datetime
from enum import Enum
from typing import AsyncGenerator, Dict, List, Literal, Optional, Sequence, Union

from bson import ObjectId
from motor.core import AgnosticCollection
from msgspec import convert, to_builtins
from pymongo import IndexModel
from typing_extensions import Self

from sshared.struct_constraints import ValidatableSturct

from .meta import Index

BasicValueType = Union[ObjectId, str, int, float, bool, None, datetime]
DocumentDictType = Dict[str, Union[BasicValueType, "DocumentDictType"]]

FilterType = Dict[str, Union[BasicValueType, Enum, "FilterType"]]
UpdateType = Dict[str, Union[BasicValueType, Enum, "UpdateType"]]
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
    def _to_document_dict(cls, data: Union[FilterType, UpdateType]) -> DocumentDictType:
        result: DocumentDictType = {}
        for key, value in data.items():
            if isinstance(value, dict):
                value = cls._to_document_dict(value)
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

        await cls.get_collection().create_indexes(index_models)

    @classmethod
    def from_dict(cls, data: DocumentDictType, /) -> Self:
        return convert(data, type=cls)

    def to_dict(self) -> DocumentDictType:
        return to_builtins(self, builtin_types=(ObjectId, datetime))

    async def save(self) -> None:
        await self.__class__.insert_one(self)

    @classmethod
    async def find_one(
        cls,
        filter: Optional[FilterType] = None,  # noqa: A002
        /,
        *,
        sort: Optional[SortType] = None,
    ) -> Optional[Self]:
        cursor = (
            cls.get_collection()
            .find(cls._to_document_dict(filter) if filter else {})
            .limit(1)
        )
        if sort:
            cursor = cursor.sort(cls._sort(sort))

        try:
            return cls.from_dict(await cursor.__anext__())
        except StopAsyncIteration:
            return None

    @classmethod
    async def find_many(
        cls,
        filter: Optional[FilterType] = None,  # noqa: A002
        /,
        *,
        sort: Optional[SortType] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> AsyncGenerator[Self, None]:
        cursor = cls.get_collection().find(
            cls._to_document_dict(filter) if filter else {}
        )
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
        await cls.get_collection().insert_one(data.to_dict())

    @classmethod
    async def insert_many(cls, data: Sequence[Self], /) -> None:
        await cls.get_collection().insert_many(x.to_dict() for x in data)

    @classmethod
    async def count(
        cls,
        filter: Optional[FilterType] = None,  # noqa: A002
        /,
        *,
        fast: bool = False,
    ) -> int:
        if fast:
            if filter:
                raise ValueError("文档数量估计值只能在无筛选条件时使用")

            return await cls.get_collection().estimated_document_count()

        return await cls.get_collection().count_documents(
            cls._to_document_dict(filter) if filter else {}
        )

    @classmethod
    async def update_one(cls, filter: FilterType, update: UpdateType, /) -> None:  # noqa: A002
        await cls.get_collection().update_one(
            cls._to_document_dict(filter), cls._to_document_dict(update)
        )

    @classmethod
    async def update_many(cls, filter: FilterType, update: UpdateType, /) -> None:  # noqa: A002
        await cls.get_collection().update_many(
            cls._to_document_dict(filter), cls._to_document_dict(update)
        )

    @classmethod
    async def delete_one(cls, filter: FilterType, /) -> None:  # noqa: A002
        await cls.get_collection().delete_one(cls._to_document_dict(filter))

    @classmethod
    async def delete_many(cls, filter: FilterType, /) -> None:  # noqa: A002
        await cls.get_collection().delete_many(cls._to_document_dict(filter))

    @classmethod
    async def aggregate_one(
        cls, pipeline: Sequence[DocumentDictType]
    ) -> Optional[DocumentDictType]:
        try:
            await cls.get_collection().aggregate(pipeline).__anext__()  # type: ignore
        except StopAsyncIteration:
            return None

    @classmethod
    async def aggregate_many(
        cls, pipeline: Sequence[DocumentDictType]
    ) -> AsyncGenerator[DocumentDictType, None]:
        async for item in cls.get_collection().aggregate(pipeline):  # type: ignore
            yield item
