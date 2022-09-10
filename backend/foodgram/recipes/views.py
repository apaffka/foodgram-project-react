import io

import reportlab
from api.filters import RecipesFilter
from api.permissions import IsAuthorOrReadOnly
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from foodgram.settings import BASE_DIR
from recipes.models import (Favourites, Ingredients, RecipeIngredient, Recipes,
                            RecipeTag, Shoplist, Tags)
from recipes.serializers import (FavouriteSerializer, IngredientsSerializer,
                                 RecipeAddUpdateSerializer, RecipesSerializer,
                                 ShoppingSerializer, TagSerializer)
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import mixins, status, views, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


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

    def create(self, request, *args, **kwargs):
        request.data['author'] = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ingredients = serializer.validated_data.pop('ingredients')
        instance = serializer.save(author=request.user)
        for ing in ingredients:
            RecipeIngredient.objects.bulk_create([RecipeIngredient(
                recipes=instance,
                amount=ing['amount'],
                ingredients=ing['ingredients'])])
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer, *args, **kwargs):
        serializer.save(serializer.validated_data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        ingredients = serializer.validated_data.pop('ingredients')
        tags = serializer.validated_data.pop('tags')
        RecipeIngredient.objects.filter(recipes=instance).delete()
        RecipeTag.objects.filter(recipes=instance).delete()
        instance.name = serializer.validated_data.pop('name')
        instance.text = serializer.validated_data.pop('text')
        if serializer.validated_data.get('image') is not None:
            instance.image = serializer.validated_data.pop('image')
        instance.cooking_time = serializer.validated_data.pop('cooking_time')
        instance.tags.set(tags)
        for ing in ingredients:
            RecipeIngredient.objects.bulk_create([RecipeIngredient(
                recipes=instance,
                amount=ing['amount'],
                ingredients=ing['ingredients'])])
        self.perform_update(serializer)
        return Response(serializer.data)


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
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer, *args, **kwargs):
        serializer.save(serializer.validated_data)

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
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer, *args, **kwargs):
        serializer.save(serializer.validated_data)

    def destroy(self, request, *args, **kwargs):
        favourite = kwargs.get('id')
        if Shoplist.objects.filter(user=request.user.id, recipe=favourite):
            Shoplist.objects.filter(
                user=request.user.id,
                recipe=favourite
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ShopListDownload(views.APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request):
        data = {}
        ingredients = RecipeIngredient.objects.filter(
            recipes__shop_list__user=request.user
        )
        # Проверяем, есть ли данные в списке
        if len(ingredients) == 0:
            return Response('В списке покупок нет данных!')

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
