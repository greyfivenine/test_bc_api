import hashlib
import uuid

from django.db import models

from application import api_blockchain


class Token(models.Model):
    """
    Модель для хранения информации о токенах.
    """
    tx_hash = models.TextField('Адрес транзакции', max_length=64, null=True, blank=True)
    owner_address = models.CharField('Адрес владельца', max_length=64, null=False, blank=False)
    unique_hash = models.CharField('Хеш токена', max_length=20, null=False, blank=False, unique=True)
    media_url = models.URLField('Ссылка на медиа', max_length=200, null=False, blank=False)

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'NFT Токен'
        verbose_name_plural = 'NFT Токены'
        db_table = 'crypto_token'
        abstract = False

    def __str__(self):
        return f'Token id: {self.id}(owner address: {self.owner_address})'

    @classmethod
    def _generate_unique_hash(cls):
        """
        Генерация уникального хеша длинной 20 символов.
        """
        unique_id = uuid.uuid4().hex

        hash_object = hashlib.sha256(unique_id.encode())

        return hash_object.hexdigest()[:20]

    @classmethod
    def create_for(cls, *args, **kwargs):
        """
        Создание инстанса модели Token с последующим деплоем в БЧ.
        """
        unique_hash = cls._generate_unique_hash()
        instance = cls.objects.create(**kwargs, unique_hash=unique_hash)
        created = True

        tx_hash = api_blockchain.mint_nft(
            instance.owner_address,
            instance.unique_hash,
            instance.media_url,
        )

        instance.tx_hash = tx_hash
        instance.save()

        return instance, created
