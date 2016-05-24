from rest_framework.serializers import Field


class S3Field(Field):
    def to_internal_value(self, value):
        return value

    def to_representation(self, value):
        return value.url
