# src/bug_generator/strategies/base_strategy.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseBugStrategy(ABC):
    """
    Lớp cơ sở trừu tượng (Interface) cho tất cả các chiến lược tạo lỗi.
    Mỗi lớp con kế thừa từ đây phải hiện thực hóa phương thức apply().
    """

    @abstractmethod
    def apply(self, program_dict: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        """
        Áp dụng logic tạo lỗi vào dictionary của chương trình.

        Args:
            program_dict: Dictionary đại diện cho cấu trúc chương trình.
            config: Cấu hình chi tiết cho việc tạo lỗi.
        """
        pass
