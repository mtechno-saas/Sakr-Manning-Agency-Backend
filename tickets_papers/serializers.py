# from rest_framework import serializers
# from .models import TravelingPaper, Ticket

# class TravelingPaperSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TravelingPaper
#         fields = '__all__'


# class TicketSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Ticket
#         fields = '__all__'


from rest_framework import serializers
from .models import TravelingPaper, Ticket

class TicketSerializer(serializers.ModelSerializer):
    # Make the file URL absolute for easier use in frontends
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        # List fields explicitly for clarity and security
        fields = [
            'id',
            'user',
            'ticket_number',
            'file',
            'file_url', # The new computed URL field
            'created_at'
        ]
        # Make 'created_at' and 'file_url' read-only
        read_only_fields = ['created_at', 'file_url']

    def get_file_url(self, obj):
        """
        Return the full URL for the file.
        """
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class TravelingPaperSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = TravelingPaper
        fields = [
            'id',
            'user',
            'title',
            'issued_date',
            'file',
            'file_url',
            'created_at'
        ]
        read_only_fields = ['created_at', 'file_url']

    def get_file_url(self, obj):
        """
        Return the full URL for the file.
        """
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None
