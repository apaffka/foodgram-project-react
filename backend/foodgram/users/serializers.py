import re

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password as pass_v
from recipes.models import Follow, Recipes
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
        if pass_v(value) is False:
            raise serializers.ValidationError()
        return make_password(value)

    def validate_first_name(self, value):
        return value.capitalize()

    def validate_last_name(self, value):
        return value.capitalize()

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
        if pass_v(value) is False:
            raise serializers.ValidationError(
                'Пароль не удовлетворяет требованиям.'
            )
        return make_password(value)


# RecipeSmallSerializer создан повторно в этом файле, чтобы избежать проблемы
# цикличных импортов
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

    # def create(self, validated_data):
    #     user = validated_data.pop('user')
    #     author = validated_data.pop('author')
    #     follow = Follow.objects.create(user=user, author=author)
    #     follow.save()
    #     return follow

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
