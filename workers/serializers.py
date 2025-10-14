from typing import Any, Dict, Optional, List, cast

from rest_framework import serializers
from rest_framework.request import Request

from .models import Worker

class WorkerListCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра и создания работников."""
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Worker
        fields = [
            'id', 'first_name', 'middle_name', 'last_name', 'email', 'position', 'is_active', 'created_by',
        ]
        read_only_fields = ['id', 'created_by']

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        request = cast(Optional[Request], self.context.get('request'))

        if request and request.method == 'GET':
            keep: set[str] = {'id', 'first_name', 'middle_name', 'last_name', 'position', 'is_active'}
            for name in list(self.fields.keys()):
                if name not in keep:
                    self.fields.pop(name)

        if request and request.method == 'POST':
            self.fields['email'].required = True

class WorkerRetrieveSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра одного работника."""

    class Meta:
        model = Worker
        fields = '__all__'


class WorkerUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для корректировки данных работника."""

    class Meta:
            model = Worker
            fields = [
                'first_name', 'middle_name', 'last_name',
                'position', 'is_active',
            ]
            extra_kwargs = {
                'first_name': {'required': False},
                'middle_name': {'required': False},
                'last_name': {'required': False},
                'position': {'required': False},
                'is_active': {'required': False},
            }

class WorkerImportRowSerializer(serializers.Serializer):
    """Сериализатор для валидации одной строки из Excel при импорте."""
    first_name = serializers.CharField(max_length=25)
    middle_name = serializers.CharField(max_length=25, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=25)
    email = serializers.EmailField()
    position = serializers.CharField(max_length=50)
    is_active = serializers.BooleanField(required=False, default=True)

    def to_worker_kwargs(self) -> Dict[str, Any]:
        data = self.validated_data
        return  {
            'first_name': data.get('first_name'),
            'middle_name': data.get('middle_name', ''),
            'last_name': data.get('last_name'),
            'email': data.get('email'),
            'position': data.get('position'),
            'is_active': data.get('is_active', True),
        }

class ImportFileSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, file):
        name = getattr(file, 'name', '')
        if not name.lower().endswith('xlsx'):
            raise serializers.ValidationError('Допустимый формат файла .xlsx')
        if file.size and file.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('Максимальный допустимый размер файла 5MB')
        return file
