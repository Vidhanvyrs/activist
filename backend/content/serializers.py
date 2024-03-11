from typing import Any, Dict, Union

from django.utils.translation import gettext as _
from rest_framework import serializers

from events.models import Format
from PIL import Image as PilImage
from utils.utils import (
    validate_creation_and_deletion_dates,
    validate_creation_and_deprecation_dates,
    validate_empty,
    validate_object_existence,
)

from .models import Faq, Image, Resource, ResourceTopic, ResourceTag,  Task, Topic, TopicFormat, Tag


class FaqSerializer(serializers.ModelSerializer[Faq]):
    class Meta:
        model = Faq
        fields = ["id", "question", "org_id", "answer", "last_updated"]

    def validate(self, data: Dict[str, Union[str, int]]) -> Dict[str, Union[str, int]]:
        validate_empty(data["question"], "question")
        validate_object_existence("entities.Organization", data["org_id"])

        return data


class ResourceSerializer(serializers.ModelSerializer[Resource]):
    class Meta:
        model = Resource
        fields = [
            "name",
            "description",
            "topics",
            "category",
            "url",
            "private",
            "created_by",
            "creation_date",
            "last_updated",
            "total_flags",
        ]

    def validate(self, data: Dict[str, Union[str, Any]]) -> Dict[str, Union[str, Any]]:
        if total_flags := data.get("total_flags") is not None:
            if not isinstance(total_flags, int):
                raise serializers.ValidationError(
                    _("Total flags must be an integer value.")
                )
            
        return data


class TaskSerializer(serializers.ModelSerializer[Task]):
    class Meta:
        model = Task
        fields = "__all__"

    def validate(self, data: Dict[str, Union[str, int]]) -> Dict[str, Union[str, int]]:
        validate_empty(data["name"], "name")
        validate_empty(data["description"], "description")
        validate_creation_and_deletion_dates(data)

        return data


class TopicSerializer(serializers.ModelSerializer[Topic]):
    class Meta:
        model = Topic
        fields = "__all__"

    def validate(self, data: Dict[str, Union[str, int]]) -> Dict[str, Union[str, int]]:
        validate_empty(data["name"], "name")
        validate_empty(data["description"], "description")

        if data["active"] is True and data["deprecation_date"] is not None:
            raise serializers.ValidationError(
                "Active topics cannot have a deprecation date."
            )

        if data["active"] is False and data["deprecation_date"] is None:
            raise serializers.ValidationError(
                "Inactive topics must have a deprecation date."
            )

        validate_creation_and_deprecation_dates(data)

        return data
    
class TagSerializer(serializers.ModelSerializer[Tag]):
    class Meta:
        model = Tag
        fields = "__all__"

    def validate(self, data: Dict[str, Union[str, int]]) -> Dict[str, Union[str, int]]:
        validate_empty(data["text"], "text")

        return data


class ResourceTopicSerializer(serializers.ModelSerializer[ResourceTopic]):
    class Meta:
        model = ResourceTopic
        fields = "__all__"

    def validate(self, data: Dict[str, Union[str, int]]) -> Dict[str, Union[str, int]]:
        validate_object_existence(Resource, data["resource_id"])
        validate_object_existence(Topic, data["topic_id"])

        return data


class ResourceTagSerializer(serializers.ModelSerializer[ResourceTag]):
    class Meta:
        model = ResourceTag
        fields = "__all__"

    def validate(self, data: Dict[str, Union[str, int]]) -> Dict[str, Union[str, int]]:
        validate_object_existence(Resource, data["resource_id"])
        validate_object_existence(Tag, data["tag_id"])

        return data

class TopicFormatSerializer(serializers.ModelSerializer[TopicFormat]):
    class Meta:
        model = TopicFormat
        fields = "__all__"

    def validate(self, data: Dict[str, Union[str, int]]) -> Dict[str, Union[str, int]]:
        validate_object_existence(Topic, data["topic_id"])
        validate_object_existence(Format, data["format_id"])

        return data

# TODO: implement the Discussion models and then import them here, as also the DiscussionTag model.
    
# class DiscussionTagSerializer(serializers.ModelSerializer[DiscussionTag]):
#     class Meta:
#         model = DiscussionTag
#         fields = "__all__"

#     def validate(self, data: Dict[str, Union[str, int]]) -> Dict[str, Union[str, int]]:
#         validate_object_existence(Discussion, data["discussion_id"])
#         validate_object_existence(Tag, data["tag_id"])

#         return data


class ImageSerializer(serializers.ModelSerializer[Image]):
    class Meta:
        model = Image
        fields = ["id", "image_location", "creation_date"]
        read_only_fields = ["id", "creation_date"]

    def validate(self, data: Dict[str, Union[str, int]]) -> Dict[str, Union[str, int]]:

        if not data["image_location"].name.endswith((".jpg", ".jpeg", ".png")):
            raise serializers.ValidationError(
                _("The image must be in .jpg, .jpeg, or .png format."), 
                code="invalid_file"
            )
        
        # TODO: check what is the maximum size of an image that we want to allow.
        if data["image_location"].size > 10485760:
            raise serializers.ValidationError(
                _("The image must be less than 10MB in size."), 
                code="invalid_file"
            )
        
        try:
            with PilImage.open(data["image_location"]) as img:
                img.verify()
        except Exception:
            raise serializers.ValidationError(
                _("The image is not valid."), 
                code="corrupted_file"
            )
       
        return data
        