from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from communer.models import User, Project, Task


class UserRegistrySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'role', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        instance = User.objects.create(username=validated_data['username'].strip(),
                                       first_name=validated_data['first_name'].strip(),
                                       last_name=validated_data['last_name'].strip(), role=validated_data['role'])
        instance.set_password(raw_password=validated_data['password'])
        instance.save()
        return instance


class ProjectSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Project
        fields = '__all__'


class ProjectTasksSerializer(serializers.ModelSerializer):
    creator = UserRegistrySerializer()
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'

    def get_tasks(self, obj):
        print(obj)
        return TaskInProjectSerializer(Task.objects.filter(project=obj), many=True).data


class TaskInProjectSerializer(serializers.ModelSerializer):
    assignee = UserRegistrySerializer()

    class Meta:
        model = Task
        fields = ['id', 'assignee', 'name', 'description', 'submit_date']


class TaskSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()
    assignee = UserRegistrySerializer()
    creator = UserRegistrySerializer()

    class Meta:
        model = Task
        fields = '__all__'


class TaskCreateSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    assignee = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False,
                                                  default=serializers.CurrentUserDefault())
    creator = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Task
        fields = '__all__'

    def validate(self, attrs):
        if attrs['creator'].role == 1:
            if attrs['assignee'].role != 2:
                raise ValidationError({'assignee': 'Assignee should be a developer'})
            if attrs['project'].creator != attrs['creator']:
                raise PermissionError('You dont have permission to create task for this project')
        else:
            if not Project.objects.filter(task__assignee=attrs['creator']).exists():
                raise PermissionError('You dont have permission to create task for this project')
            attrs['assignee'] = attrs['creator']
        return attrs

    def create(self, validated_data):
        if validated_data['creator'].role == 2:
            validated_data['assignee'] = validated_data['creator']
        instance = Task.objects.create(**validated_data)
        return instance
