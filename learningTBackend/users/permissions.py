from rest_framework.permissions import BasePermission

# STEP : Protect test generation + trial enforcement
# ===============================================


# Goal:
# - Only authenticated users can generate tests
# - Free users can generate up to 5 tests
# - Premium / Gold users bypass trial limits


class CanGenerateTest(BasePermission):
    """
    Allows test generation if:
    - user is authenticated AND
    - user has trials left OR has premium access
    """


    message = 'Trial limit exceeded. Please upgrade your plan.'


    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False


        if user.has_premium_access():
            return True


        return user.has_trials_left()