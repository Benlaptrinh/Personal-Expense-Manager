import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class CategoryType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
