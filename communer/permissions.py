from rest_framework.permissions import IsAuthenticated


class IsPMUser(IsAuthenticated):

    def has_permission(self, request, view):
        has_perm = super(IsPMUser, self).has_permission(request, view)
        return has_perm and request.user.role == 1


class IsDevUser(IsAuthenticated):

    def has_permission(self, request, view):
        has_perm = super(IsDevUser, self).has_permission(request, view)
        return has_perm and request.user.role == 2
