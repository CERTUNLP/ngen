import copy
from rest_framework.permissions import DjangoModelPermissions, BasePermission


class CustomModelPermissions(DjangoModelPermissions):

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)  # from EunChong's answer
        self.perms_map["GET"] = ["%(app_label)s.view_%(model_name)s"]


class CustomModelPermissionsOrMinified(DjangoModelPermissions):

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)  # from EunChong's answer
        self.perms_map["GET"] = [
            "%(app_label)s.view_%(model_name)s",
            "%(app_label)s.view_minified_%(model_name)s",
        ]

    def has_permission(self, request, view):
        if not request.user or (
            not request.user.is_authenticated and self.authenticated_users_only
        ):
            return False

        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, "_ignore_model_permissions", False):
            return True

        queryset = self._queryset(view)
        perms = self.get_required_permissions(request.method, queryset.model)

        return any(request.user.has_perm(perm) for perm in perms)


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


class ActionPermission(BasePermission):
    """
    Generic permission that checks if the user has the permission specified in the action.
    """

    def has_permission(self, request, view):
        # Obtains the required permission from action_permissions attribute of the view
        required_permission = getattr(view, "action_permissions", {}).get(
            request.method
        )

        # If there is no permission defined, allow access
        if not required_permission:
            return True

        # Check if the user has the required permission
        return request.user.has_perm(required_permission)
