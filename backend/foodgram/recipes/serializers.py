from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favourites, Ingredients, RecipeIngredient, Recipes,
                            Shoplist, Tags)
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = '__all__'


class IngredientsForRecipeSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredients
        fields = '__all__'

    def get_amount(self, obj):
        amount = RecipeIngredient.objects.filter(
            ingredients=obj).values_list('amount', flat=True)
        return amount[0]


class IngredientAddToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(),
        source='ingredients'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeAddUpdateSerializer(serializers.ModelSerializer):
    ingredients = IngredientAddToRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tags.objects.all()
    )
    image = Base64ImageField(max_length=None)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipes
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def validate_cooking_time(self, data):
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) <= 0:
            raise serializers.ValidationError(
                'Должно быть больше нуля'
            )
        return data

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        for ing in ingredients:
            if int(ing['amount']) <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше нуля'
                )
        return data

    def to_representation(self, instance):
        representation = RecipesSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data
        return representation


class RecipesSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=False, many=True)
    author = UserSerializer(read_only=True, many=False)
    ingredients = IngredientsForRecipeSerializer(many=True, required=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None)
    pub_date = serializers.DateTimeField(write_only=True, required=False)

    class Meta:
        model = Recipes
        fields = '__all__'

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Favourites.objects.filter(recipe=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Shoplist.objects.filter(recipe=obj, user=user).exists()


class RecipeSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class FavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourites
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favourites.objects.all(),
                fields=('user', 'recipe'),
                message='Вы уже добавили рецепт с список избранного'
            )
        ]

    # def create(self, validated_data):
    #     user = validated_data.pop('user')
    #     recipe = validated_data.pop('recipe')
    #     favourite = Favourites.objects.create(user=user, recipe=recipe)
    #     favourite.save()
    #     return favourite

    def to_representation(self, instance):
        representation = RecipeSmallSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
        return representation


class ShoppingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shoplist
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Shoplist.objects.all(),
                fields=('user', 'recipe'),
                message='Вы уже добавили рецепт в список покупок'
            )
        ]

    # def create(self, validated_data):
    #     user = validated_data.pop('user')
    #     recipe = validated_data.pop('recipe')
    #     favourite = Shoplist.objects.create(user=user, recipe=recipe)
    #     favourite.save()
    #     return favourite

    def to_representation(self, instance):
        representation = RecipeSmallSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
        return representation
