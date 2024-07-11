from rest_framework import serializers


class OrganizationDocumentSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    website = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    country = serializers.CharField(read_only=True)
    industry = serializers.CharField(read_only=True)
    organization_id = serializers.CharField(read_only=True)

    year_founded = serializers.IntegerField(read_only=True)
    number_of_employees = serializers.IntegerField(read_only=True)

    class Meta:
        fields = (
            'name',
            'website',
            'description',
            'country',
            'industry',
            'organization_id',
            'year_founded',
            'number_of_employees',
        )

        read_only_fields = fields
