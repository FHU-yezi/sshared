from datetime import datetime
from enum import Enum
from typing import AsyncGenerator, Dict, List, Literal, Optional, Sequence, Union

from bson import ObjectId
from motor.core import AgnosticCollection
from msgspec import convert, to_builtins
from msgspec.inspect import type_info
from pymongo import IndexModel
from typing_extensions import Self

from sshared.struct import ValidatableSturct

from .meta import Index

BasicValueType = Union[ObjectId, str, int, float, bool, None, datetime]

DbDocumentType = Dict[str, Union[BasicValueType, "DbDocumentType"]]
FilterType = Dict[object, Union[BasicValueType, Enum]]
UpdateType = Dict[object, Union[BasicValueType, Enum, "UpdateType"]]
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
    def _field_name(cls, field: object, /) -> str:
        # 若没有 __qualname__ 属性，则 field 是一个 str
        # 此时直接返回
        if not hasattr(field, "__qualname__"):
            return field  # type: ignore

        name_parts = field.__qualname__.split(".")

        if name_parts[0] != cls.__name__:
            raise ValueError(f"字段 {field.__qualname__} 不属于该文档模型")
        if len(name_parts) != 2:
            raise NotImplementedError("暂不支持获取嵌套字段的名称")

        attr_name = name_parts[1]
        # 迭代当前文档模型的每个字段，找到对应字段的名称并返回
        for field_obj in type_info(cls).fields:  # type: ignore
            if field_obj.name != attr_name:
                continue

            return field_obj.encode_name

        raise AssertionError("未找到属性对应的字段名称")

    @classmethod
    def _filter(cls, filter: FilterType, /) -> Dict[str, BasicValueType]:  # noqa: A002
        result: Dict[str, BasicValueType] = {}
        for key, value in filter.items():
            key = cls._field_name(key)
            if isinstance(value, Enum):
                value = value.value

            result[key] = value

        return result

    @classmethod
    def _update(cls, update: UpdateType, /) -> Dict[str, BasicValueType]:
        result: Dict[str, BasicValueType] = {}
        for key, value in update.items():
            key = cls._field_name(key)
            if isinstance(value, Enum):
                value = value.value
            if isinstance(value, dict):
                value = cls._update(value)

            result[key] = value  # type: ignore

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
    def from_db(cls, data: DbDocumentType, /) -> Self:
        return convert(data, type=cls)

    def to_db(self) -> DbDocumentType:
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
            cls.get_collection().find(cls._filter(filter) if filter else {}).limit(1)
        )
        if sort:
            cursor = cursor.sort(cls._sort(sort))

        try:
            return cls.from_db(await cursor.__anext__())
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
        cursor = cls.get_collection().find(cls._filter(filter) if filter else {})
        if sort:
            cursor = cursor.sort(cls._sort(sort))
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)

        async for item in cursor:
            yield cls.from_db(item)

    @classmethod
    async def insert_one(cls, data: Self, /) -> None:
        await cls.get_collection().insert_one(data.to_db())

    @classmethod
    async def insert_many(cls, data: Sequence[Self], /) -> None:
        await cls.get_collection().insert_many(x.to_db() for x in data)

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
            cls._filter(filter) if filter else {}
        )

    @classmethod
    async def update_one(cls, filter: FilterType, update: UpdateType, /) -> None:  # noqa: A002
        await cls.get_collection().update_one(cls._filter(filter), cls._update(update))

    @classmethod
    async def update_many(cls, filter: FilterType, update: UpdateType, /) -> None:  # noqa: A002
        await cls.get_collection().update_many(cls._filter(filter), cls._update(update))

    @classmethod
    async def delete_one(cls, filter: FilterType, /) -> None:  # noqa: A002
        await cls.get_collection().delete_one(cls._filter(filter))

    @classmethod
    async def delete_many(cls, filter: FilterType, /) -> None:  # noqa: A002
        await cls.get_collection().delete_many(cls._filter(filter))
