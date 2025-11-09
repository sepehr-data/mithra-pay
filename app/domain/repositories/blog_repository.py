# app/domain/repositories/blog_repository.py
from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.blog_post import BlogPost


class IBlogRepository(ABC):
    """
    Blog / Mag repository interface.
    """

    @abstractmethod
    def get_by_id(self, post_id: int) -> Optional[BlogPost]:
        ...

    @abstractmethod
    def get_by_slug(self, slug: str) -> Optional[BlogPost]:
        ...

    @abstractmethod
    def list_posts(
        self,
        is_published: Optional[bool] = True,
        limit: int = 50,
        offset: int = 0,
    ) -> List[BlogPost]:
        ...

    @abstractmethod
    def create(self, post: BlogPost) -> BlogPost:
        ...

    @abstractmethod
    def update(self, post: BlogPost) -> BlogPost:
        ...
