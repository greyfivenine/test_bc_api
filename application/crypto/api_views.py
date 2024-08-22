from django.shortcuts import Http404, redirect
from django.utils.decorators import method_decorator

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body

from application.api.views import PaginatedResponseMixin
from application import api_blockchain

from . import (
    models as token_models,
    serializers as token_serializers,
)


ERROR_RESPONSE = {
    'status': 'error',
    'details': None,
}


CRYPTO_TOKEN_TAGS = ['Крипто токены']


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary='Список крипто токенов.',
    tags=CRYPTO_TOKEN_TAGS,
    responses={
        200: token_serializers.TokenSerializer,
        400: 'Bad request',
    },
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary='Детали крипто токена.',
    operation_description='Детали крипто токена.',
    tags=CRYPTO_TOKEN_TAGS,
    responses={
        200: token_serializers.TokenSerializer,
        400: 'Bad request',
    },
))
class TokenViewSet(PaginatedResponseMixin, viewsets.ReadOnlyModelViewSet):
    """
    Набор апи-методов для работы крипто токенами.
    """
    serializer_class = token_serializers.TokenSerializer
    queryset_class = token_models.Token

    def get_queryset(self):
        return self.queryset_class.objects.all()

    def list(self, request, *args, **kwargs):
        """
        Получение списка токенов с пагинированным ответом.
        """
        queryset = self.get_queryset()

        return self.get_paginated_ads_response(queryset)

    @swagger_auto_schema(
        operation_summary='Создание крипто токена.',
        methods=['post'],
        tags=CRYPTO_TOKEN_TAGS,
        responses={
            201: token_serializers.TokenSerializer,
            400: 'Bad request',
        },
    )
    @action(
        detail=False,
        methods=['post'],
        url_path='create',
    )
    def create_token(self, request, *args, **kwargs):
        """
        Создание крипто токена.
        """
        ser = token_serializers.TokenSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        data = ser.validated_data

        instance, created = token_models.Token.create_for(**data)

        return Response(
            {
                'status': created,
                'created': token_serializers.TokenSerializer(instance).data,
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary='Получить total_supply токена.',
        methods=['get'],
        tags=CRYPTO_TOKEN_TAGS,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                title='total_supply',
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description='status'),
                    'total_supply': openapi.Schema(type=openapi.TYPE_NUMBER, description='total_supply'),
                },
            ),
            404: 'Not found',
        },
    )
    @action(
        detail=False,
        methods=['get'],
        url_path='total_supply',
    )
    def get_total_supply(self, request, *args, **kwargs):
        """
        Получение total_supply токена.
        """
        contract = api_blockchain.get_nft_contract()

        try:
            total_supply = api_blockchain.get_total_supply(contract)
        except ValueError as e:
            ERROR_RESPONSE['details'] = e
            raise Http404(ERROR_RESPONSE)

        return Response(
            {
                'status': 'Ok',
                'total_supply': total_supply,
            },
            status=status.HTTP_200_OK,
        )
