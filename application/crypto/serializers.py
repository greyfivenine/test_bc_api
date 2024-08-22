from rest_framework import serializers

from . import (
    models as crypto_models,
)


class TokenSerializer(serializers.ModelSerializer):
    """
    Сериализатор ADS компании для редактирования.
    """
    class Meta:
        model = crypto_models.Token
        fields = '__all__'
        read_only_fields = ['id', 'tx_hash', 'unique_hash']

    def get_tx_hash(self, obj, *args, **kwargs):
        if obj.tx_hash is not None:
            return f'0x{obj.tx_hash}'
