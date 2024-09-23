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
