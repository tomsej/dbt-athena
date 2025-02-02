from dataclasses import dataclass

from dbt.adapters.athena.relation import TableType
from dbt.adapters.base.column import Column
from dbt.exceptions import DbtRuntimeError


@dataclass
class AthenaColumn(Column):
    table_type: TableType = TableType.TABLE

    def is_iceberg(self) -> bool:
        return self.table_type == TableType.ICEBERG

    def is_string(self) -> bool:
        return self.dtype.lower() in {"varchar", "string"}

    def is_binary(self) -> bool:
        return self.dtype.lower() in {"binary", "varbinary"}

    def is_timestamp(self) -> bool:
        return self.dtype.lower() in {"timestamp"}

    @classmethod
    def string_type(cls, size: int) -> str:
        return f"varchar({size})" if size > 0 else "varchar"

    @classmethod
    def binary_type(cls) -> str:
        return "varbinary"

    def timestamp_type(self) -> str:
        if self.is_iceberg():
            return "timestamp(6)"
        return "timestamp"

    def string_size(self) -> int:
        if not self.is_string():
            raise DbtRuntimeError("Called string_size() on non-string field!")
        if not self.char_size:
            # Handle error: '>' not supported between instances of 'NoneType' and 'NoneType' for union relations macro
            return 0
        return self.char_size

    @property
    def data_type(self) -> str:
        if self.is_string():
            return self.string_type(self.string_size())
        elif self.is_numeric():
            return self.numeric_type(self.dtype, self.numeric_precision, self.numeric_scale)
        elif self.is_binary():
            return self.binary_type()
        elif self.is_timestamp():
            return self.timestamp_type()
        return self.dtype
