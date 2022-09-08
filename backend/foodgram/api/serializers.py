import re

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import \
    validate_password as pass_valid
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favourites, Follow, Ingredients, RecipeIngredient,
                            Recipes, RecipeTag, Shoplist, Tags)
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )
        lookup_field = 'id'

    def validate_username(self, value):
        value_lower = value.lower()
        regex = r'^[\w.@+-]+\Z'
        if re.match(regex, value_lower) is None:
            raise serializers.ValidationError(
                'Введены недопустимые символы.'
            )
        elif User.objects.filter(username=value_lower):
            raise serializers.ValidationError(
                'Имя пользователя занято. Придумайте другое.'
            )
        elif value_lower == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать имя me в качестве имени пользователя.'
            )
        return value_lower

    def validate_password(self, value):
        if pass_valid(value) is False:
            raise serializers.ValidationError()
        return make_password(value)

    def validate_first_name(self, value):
        capital_value = value.capitalize()
        return capital_value

    def validate_last_name(self, value):
        capital_value = value.capitalize()
        return capital_value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['email'] = instance.email.lower()
        representation['first_name'] = instance.first_name.capitalize()
        representation['last_name'] = instance.last_name.capitalize()
        return representation

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Follow.objects.filter(user=user, author=obj).exists()


class ChangePasswordSerializer(serializers.Serializer):
    model = User
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        current_password = self.context['request'].user.password
        if check_password(value, current_password) is False:
            raise serializers.ValidationError(
                'Вы ввели неправильный текущий пароль. Попробуйте снова.'
            )
        return value

    def validate_new_password(self, value):
        if pass_valid(value) is False:
            raise serializers.ValidationError(
                'Пароль не удовлетворяет требованиям.'
            )
        return make_password(value)


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

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipes.objects.create(author=request.user, **validated_data)
        recipe.save()
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipes=recipe,
                amount=ingredient['amount'],
                ingredients=ingredient['ingredients']
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        RecipeIngredient.objects.filter(recipes=instance).delete()
        RecipeTag.objects.filter(recipes=instance).delete()
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        if validated_data.get('image') is not None:
            instance.image = validated_data.pop('image')
        instance.cooking_time = validated_data.pop('cooking_time')
        instance.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipes=instance,
                amount=ingredient['amount'],
                ingredients=ingredient['ingredients']
            )
        return instance

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


class UserSmallSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        lookup_field = 'id'

    def get_recipes(self, obj):
        recipes = obj.recipes.all()[:3]
        return RecipeSmallSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Follow.objects.filter(user=user, author=obj).exists()


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('author',)

    def to_representation(self, instance):
        request = self.context.get('request')
        return UserSmallSerializer(
            instance.author,
            context={'request': request}
        ).data


class FollowAddSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны'
            )
        ]

    def create(self, validated_data):
        user = validated_data.pop('user')
        author = validated_data.pop('author')
        follow = Follow.objects.create(user=user, author=author)
        follow.save()
        return follow

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError("На себя нельзя подписаться")
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return UserSmallSerializer(
            instance.author,
            context={'request': request}
        ).data


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

    def create(self, validated_data):
        user = validated_data.pop('user')
        recipe = validated_data.pop('recipe')
        favourite = Favourites.objects.create(user=user, recipe=recipe)
        favourite.save()
        return favourite

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

    def create(self, validated_data):
        user = validated_data.pop('user')
        recipe = validated_data.pop('recipe')
        favourite = Shoplist.objects.create(user=user, recipe=recipe)
        favourite.save()
        return favourite

    def to_representation(self, instance):
        representation = RecipeSmallSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
        return representation
