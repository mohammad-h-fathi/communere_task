from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.utils import unix_epoch

from communer.models import Project, User, Task
from communer.permissions import IsPMUser, IsDevUser
from communer.serializers import UserRegistrySerializer, ProjectSerializer, ProjectTasksSerializer, TaskSerializer, \
    TaskCreateSerializer


class RegisterUserView(CreateAPIView):
    serializer_class = UserRegistrySerializer
    permission_classes = [permissions.AllowAny]


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                payload = JSONWebTokenAuthentication.jwt_create_payload(user)

                return Response({
                    'token': JSONWebTokenAuthentication.jwt_encode_payload(payload),
                    'user': UserRegistrySerializer(user).data,
                    'issued_at': payload.get('iat', unix_epoch())
                })
        except User.DoesNotExist:
            pass
        return Response({'detail': 'Invalid Username or Password'}, status=status.HTTP_400_BAD_REQUEST)


class ProjectsListView(ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JSONWebTokenAuthentication]

    def get_queryset(self):
        qs = Project.objects
        if self.request.user.role == 1:
            qs = qs.filter(creator=self.request.user)
        else:
            qs = qs.filter(task__assignee=self.request.user)
        return qs


class ProjectRetrieveView(RetrieveAPIView):
    serializer_class = ProjectTasksSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JSONWebTokenAuthentication]
    queryset = Project.objects.all()

    def get_queryset(self):
        qs = super(ProjectRetrieveView, self).get_queryset()
        if self.request.user.role == 1:
            qs = qs.filter(creator=self.request.user)
        else:
            qs = qs.filter(task__assignee=self.request.user)
        return qs


class ProjectCreatorView(CreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JSONWebTokenAuthentication]


class TasksListView(ListAPIView):
    permission_classes = [IsDevUser]
    authentication_classes = [JSONWebTokenAuthentication]
    serializer_class = TaskSerializer

    def get_queryset(self):
        if self.request.user.role == 1:
            projs = Project.objects.filter(creator=self.request.user)
            qs = Task.objects.filter(project__in=projs)
        else:
            qs = Task.objects.filter(assignee=self.request.user)
        return qs


class TaskCreateView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JSONWebTokenAuthentication]
    serializer_class = TaskCreateSerializer
