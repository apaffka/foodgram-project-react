from django.shortcuts import get_object_or_404
from recipes.models import Follow
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import User
from users.serializers import (ChangePasswordSerializer, FollowAddSerializer,
                               FollowSerializer, UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['POST'],
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        username = request.user.username
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            password = serializer.data['new_password']
            User.objects.filter(username=username).update(password=password)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowSerializer

    def get_queryset(self):
        user = get_object_or_404(User, id=self.request.user.pk)
        new_queryset = user.follower.all()
        return new_queryset


class FollowAddViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Follow.objects.all()
    serializer_class = FollowAddSerializer
    http_method_names = ['post', 'delete']

    def get_serializer_context(self):
        context = super(FollowAddViewSet, self).get_serializer_context()
        context.update({'request': self.request})
        return context

    def create(self, request, *args, **kwargs):
        data_my = {
            'user': request.user.id,
            'author': kwargs.get('id')
        }
        serializer = self.get_serializer(data=data_my)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer, *args, **kwargs):
        serializer.save(serializer.validated_data)

    def destroy(self, request, *args, **kwargs):
        followed = kwargs.get('id')
        Follow.objects.filter(user=request.user.id, author=followed).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
