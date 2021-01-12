from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional, cast

from vgloss import models, serializers

@dataclass  # type: ignore
class Action(ABC):

    def serialize(self):
        return {
            "type": self.__class__.__name__,
            "data": self.__dict__,
        }

    @abstractmethod
    def do(self) -> Optional[List["Action"]]:
        raise NotImplementedError()


@dataclass
class TagUpdate(Action):
    tags: List[dict]

    def do(self) -> Optional[List[Action]]:
        # Save tags (and delete any not referenced)
        serializer = serializers.TagSerializer(data=self.tags, many=True)
        serializer.is_valid(raise_exception=True)
        # Set delete_unseen since we want to save all tags as a unit.
        # Set ignore_not_found because any integer IDs referenced must have
        # been deleted (unless the client is making up IDs that never existed.
        serializer.save(delete_unseen=True, ignore_not_found=True)

        # Retrieve saved tags
        serializer = serializers.TagSerializer(models.Tag.objects.all(), many=True)
        serialized_tags = cast(List[Dict], serializer.data)
        return [
            TagUpdate(tags=serialized_tags)
        ]


ACTION_CLASSES = {
    cls.__name__: cls for cls in [
        TagUpdate,
    ]
}
