import copy
from rest_framework.permissions import DjangoModelPermissions, BasePermission


class CustomModelPermissions(DjangoModelPermissions):

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)  # from EunChong's answer
        self.perms_map["GET"] = ["%(app_label)s.view_%(model_name)s"]


class IsSelf(BasePermission):

    def has_object_permission(self, request, view, obj):
        # Permite el acceso solo si el usuario autenticado es el mismo que el objeto
        return obj == request.user


class CustomApiViewPermission(BasePermission):
    """
    Verify a list of custom permissions.

    To use it, add a required_permissions attribute to the view class.

    Permissions must be defined in the database and can be added through
    ngen.models.common.permission.CustomPermissionSupport.

    Example:
    class MyView(APIView):
        permission_classes = [CustomApiViewPermission]
        required_permissions = ['ngen.permission_name']
    """

    def has_permission(self, request, view):
        required_permissions = getattr(view, "required_permissions", [])

        for perm in required_permissions:
            if not request.user.has_perm(perm):
                return False

        return True


class CustomMethodApiViewPermission(BasePermission):
    """
    Verify a list of custom permissions.

    To use it, add a required_permissions attribute to the view class.

    Permissions must be defined in the database and can be added through
    ngen.models.common.permission.CustomPermissionSupport.

    Returns True if method is not defined in required_permissions.

    Example:
    class MyView(APIView):
        permission_classes = [CustomMethodApiViewPermission]
        required_permissions = {
            'GET': ['ngen.permission_name'],
            'HEAD': ['ngen.permission_name'],
            # 'OPTIONS': ['ngen.permission_name'], # If is not defined, it will return True
            'POST': ['ngen.permission_name'],
            'PUT': ['ngen.permission_name'],
            'PATCH': ['ngen.permission_name'],
            'DELETE': ['not_allowed'], # If permission is not defined, it will return False
        }

    """

    def has_permission(self, request, view):
        required_permissions = getattr(view, "required_permissions", {})
        method = request.method
        for perm in required_permissions.get(method, []):
            if not request.user.has_perm(perm):
                return False

        return True
