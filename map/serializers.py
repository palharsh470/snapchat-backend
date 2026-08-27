from rest_framework import serializers
from .models import Location

class LocationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='profile.user.id', read_only=True)
    name = serializers.CharField(source='profile.user.username', read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = ['id', 'name', 'avatar', 'latitude', 'longitude', 'updated_at']
        read_only_fields = ['id', 'name', 'avatar', 'updated_at']

    def get_avatar(self, obj):
        avatar = obj.profile.avatar
        request = self.context.get('request')
        if avatar and request:
            return request.build_absolute_uri(avatar.url)
        return None