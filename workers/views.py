from typing import Any, Type

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import BaseSerializer
from rest_framework.exceptions import NotFound

from .models import Worker
from .serializers import WorkerRetrieveSerializer, WorkerListCreateSerializer, WorkerUpdateSerializer, ImportFileSerializer
from .services import WorkerService

class WorkerPagination(PageNumberPagination):
    page_size: int = 3
    page_size_query_param: str = 'page_size'
    max_page_size: int = 100

class WorkerListCreateAPIView(ListCreateAPIView):
    """Представление для просмотра и создания работников с пагинацией и фильтрацией."""
    serializer_class = WorkerListCreateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = WorkerPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'position']

    def get_queryset(self) -> QuerySet[Worker]:
        try:
            return WorkerService.get_workers()
        except Exception as error:
            raise NotFound({
                'detail': 'Ошибка получения работников'
            })

class WorkerRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """Представление для просмотра, корректировки и удаления сотрудников."""
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self) -> Type[BaseSerializer]:
        return WorkerRetrieveSerializer if self.request.method == 'GET' else WorkerUpdateSerializer

    def get_object(self) -> Worker:
        pk_raw: Any = self.kwargs.get('pk')
        try:
            pk_int: int = int(pk_raw)
        except (TypeError, ValueError):
            raise NotFound({'detail': 'Некорректный идентификатор'})

        try:
            worker: Worker = WorkerService.get_worker(pk_int)
        except Worker.DoesNotExist:
            raise NotFound({'detail': f'Сотрудника с id={pk_int} не существует.'})
        return worker

class WorkerImportAPIView(GenericAPIView):
    """Импорт работников из Excel файла."""
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ImportFileSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_obj = serializer.validated_data['file']
        result = WorkerService.import_workers_from_excel(
            file_obj,
            request.user if request.user.is_authenticated else None
        )
        return Response({
            'added': result['added'],
            'errors': result['errors'],
            'total': result['total'],
        })

        
