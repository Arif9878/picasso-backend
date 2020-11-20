from django.shortcuts import render
from rest_framework import status, viewsets, permissions
from .models import Menu, MenuType
from .serializers import MenuSerializer, MenuTypeSerializer
from rest_framework.response import Response

# Create your views here.

class MenuTypeViewSet(viewsets.ModelViewSet):
    queryset = MenuType.objects.all()
    serializer_class = MenuTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete', 'head']

    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the menu type as determined by the username portion of the URL.
        """
        return self.queryset

class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete', 'head']

    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the menu as determined by the username portion of the URL.
        """
        title = self.request.query_params.get('title', None)
        blank = ""
        if title is not None and title is not blank:
            self.queryset = self.queryset(title=title)
        return self.queryset

    def list(self, request, format=None):
        """
            List Menu
        """
        menu_type = self.request.query_params.get('menu_type', None)
        user = request.user
        blank = ""
        if user.menu:
            queryset = Menu.v1.list(menu_type=user.menu.id)
        if menu_type is not None and menu_type is not blank:
            queryset = Menu.v1.list(menu_type=menu_type)
        return Response(
            queryset,
            status=status.HTTP_200_OK)
