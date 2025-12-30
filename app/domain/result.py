# app/structural/domain/result.py
"""
Tipo Result genérico para respuestas estandarizadas.
"""
from dataclasses import dataclass
from typing import TypeVar, Generic, Optional, Any

T = TypeVar('T')


@dataclass
class Result(Generic[T]):
    """
    Resultado genérico para operaciones que pueden fallar.

    Uso:
        # Éxito
        result = Result.ok(data)
        if result.success:
            process(result.data)

        # Error
        result = Result.error("Something went wrong")
        if not result.success:
            handle_error(result.error_message)
    """
    success: bool
    data: Optional[T] = None
    error_message: Optional[str] = None

    @staticmethod
    def ok(data: T) -> 'Result[T]':
        """Crea un resultado exitoso."""
        return Result(success=True, data=data)

    @staticmethod
    def error(message: str) -> 'Result[T]':
        """Crea un resultado de error."""
        return Result(success=False, error_message=message)

    def to_dict(self) -> dict:
        """Convierte a diccionario para API responses."""
        if self.success:
            return {'success': True, 'data': self.data}
        return {'success': False, 'error': self.error_message}

    def map(self, func) -> 'Result':
        """Aplica una función al data si es éxito."""
        if self.success and self.data is not None:
            return Result.ok(func(self.data))
        return self
