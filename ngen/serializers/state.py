from ngen import models
from ngen.serializers import NgenModelSerializer


class StateSerializer(NgenModelSerializer):
    class Meta:
        model = models.State
        fields = '__all__'
        read_only_fields = ['slug']


class EdgeSerializer(NgenModelSerializer):
    class Meta:
        model = models.Edge
        fields = '__all__'
