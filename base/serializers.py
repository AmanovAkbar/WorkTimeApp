from rest_framework import serializers
from rest_framework.relations import StringRelatedField
from base.models import User, Organization, WorkTime, OrganizationWorkTime
from django.contrib.auth import authenticate


class OrganizationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


class OrganizationWorkTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationWorkTime
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    organizations = OrganizationsSerializer(many=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'organizations', 'email']


class WorkTimeSerializer(serializers.ModelSerializer):
    user = StringRelatedField  # could have done via SlugRelatedField
    duration = serializers.SerializerMethodField('get_duration')
    organization = OrganizationsSerializer

    def get_duration(self, obj):
        td = obj.end_time - obj.start_time
        return f'{td.seconds // 3600} hours, {td.seconds // 60 % 60} minutes'

    class Meta:
        model = WorkTime
        fields = '__all__'


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(
        label="Email",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
            if not user:
                msg = 'Access denied: wrong username or password.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Both "username" and "password" are required.'
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs


