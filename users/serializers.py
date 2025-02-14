from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password


User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "confirm_password", "role"]

    def validate(self, attrs):
        """Ensure password and confirm_password match."""
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"password": "Password do not match."})
        return super().validate(attrs)
    
    def create(self, validated_data):
        """Remove confirm_password before saving."""
        validated_data.pop("confirm_password")
        user = User.objects.create_user(**validated_data)
        return user
    

# import re
# class CustomUserSerializer(serializers.ModelSerializer):
#     """Serializer for the CustomUser model with additional validations."""

#     email = serializers.EmailField(
#         required=True, 
#         validators=[serializers.UniqueValidator(queryset=User.objects.all())]
#     )
#     username = serializers.CharField(
#         max_length=15,
#         required=True,
#         validators=[serializers.UniqueValidator(queryset=User.objects.all())]
#     )
#     password = serializers.CharField(write_only=True, min_length=8)

#     def validate_password(self, value):
#         """
#         Validates password strength.
#         Must contain at least one uppercase letter, one number, and one special character.
#         """
#         if not re.search(r'[A-Z]', value) or not re.search(r'[0-9]', value) or not re.search(r'[\W_]', value):
#             raise serializers.ValidationError("Password must contain at least one uppercase letter, one number, and one special character.")
#         return value

#     def create(self, validated_data):
#         """
#         Creates a new user and sets the password securely.
#         """
#         user = User.objects.create_user(**validated_data)
#         return user

#     class Meta:
#         model = User
#         fields = ("id", "email", "username", "password", "role")