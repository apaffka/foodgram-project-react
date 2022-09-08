import io

import reportlab
from api.filters import RecipesFilter
from api.permissions import IsAuthorOrReadOnly
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from foodgram.settings import BASE_DIR
from recipes.models import (Favourites, Follow, Ingredients, RecipeIngredient,
                            Recipes, Shoplist, Tags)
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import mixins, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import User

from .serializers import (ChangePasswordSerializer, FavouriteSerializer,
                          FollowAddSerializer, FollowSerializer,
                          IngredientsSerializer, RecipeAddUpdateSerializer,
                          RecipesSerializer, ShoppingSerializer, TagSerializer,
                          UserSerializer)


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


class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [SearchFilter]
    search_fields = ['name']


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipesFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return RecipeAddUpdateSerializer
        return RecipesSerializer

    def get_serializer_context(self):
        context = super(RecipesViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context


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
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        followed = kwargs.get('id')
        Follow.objects.filter(user=request.user.id, author=followed).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavouriteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Favourites.objects.all()
    serializer_class = FavouriteSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        data_my = {
            'user': request.user.id,
            'recipe': kwargs.get('id')

        }
        serializer = self.get_serializer(data=data_my)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        favourite = kwargs.get('id')
        Favourites.objects.filter(
            user=request.user.id,
            recipe=favourite
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoplistViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ShoppingSerializer
    queryset = Shoplist.objects.all()
    pagination_class = None

    def create(self, request, *args, **kwargs):
        data_my = {
            'user': request.user.id,
            'recipe': kwargs.get('id')

        }
        serializer = self.get_serializer(data=data_my)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        favourite = kwargs.get('id')
        Shoplist.objects.filter(
            user=request.user.id,
            recipe=favourite
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShopListDownload(views.APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request):
        data = {}
        ingredients = RecipeIngredient.objects.filter(
            recipes__shop_list__user=request.user
        )
        for ing in ingredients:
            name = ing.ingredients.name
            amount = ing.amount
            measurement_unit = ing.ingredients.measurement_unit
            if name not in data:
                data[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
            else:
                data[name]['amount'] += amount

        for_print = ([f"{item}: {value['amount']}"  
                      f" {value['measurement_unit']}"
                      for item, value in data.items()])

        # Готовим ReportLab для работы
        # path = str(BASE_DIR) + '/data/DejaVuSans.ttf'
        reportlab.rl_config.TTFSearchPath.append(str(BASE_DIR))
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        p.setFont('DejaVuSans', 20)
        p.drawString(20, 800, 'Для ваших рецептов нужно купить:')
        p.setFont('DejaVuSans', 14)
        iter = 0
        for i in for_print:
            p.drawString(20, 750 - iter, f'{i}')
            iter += 20
        p.setFont('DejaVuSans', 10)
        p.drawString(20, 40, 'Foodgram by Pavel Agapov, 2022')
        p.drawString(20, 25, 'All rights reserved')
        p.showPage()
        p.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='hello.pdf')