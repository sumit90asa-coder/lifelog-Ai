from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username   = request.data.get('username', '').strip()
    email      = request.data.get('email', '').strip()
    password   = request.data.get('password', '')
    password2  = request.data.get('password2', '')
    first_name = request.data.get('first_name', '').strip()
    last_name  = request.data.get('last_name', '').strip()

    # Validation
    errors = {}
    if not username:
        errors['username'] = ['Username is required.']
    elif User.objects.filter(username=username).exists():
        errors['username'] = ['Username already taken.']

    if email and User.objects.filter(email=email).exists():
        errors['email'] = ['Email already registered.']

    if not password:
        errors['password'] = ['Password is required.']
    elif len(password) < 8:
        errors['password'] = ['Password must be at least 8 characters.']

    if password != password2:
        errors['password2'] = ['Passwords do not match.']

    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )

    return Response({
        'id':         user.id,
        'username':   user.username,
        'email':      user.email,
        'first_name': user.first_name,
        'last_name':  user.last_name,
        'message':    'Account created successfully.',
    }, status=status.HTTP_201_CREATED)