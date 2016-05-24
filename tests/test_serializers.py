from buckets import fields, serializers


def test_s3_field():
    field = fields.S3FileField()
    s3_file = fields.S3File('http://example.com/file.txt', field)

    serializer_field = serializers.S3Field()
    assert serializer_field.to_internal_value(s3_file) == s3_file
    assert serializer_field.to_representation(s3_file) == s3_file.url
