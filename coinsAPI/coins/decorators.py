from django_ratelimit.decorators import ratelimit
from functools import wraps
from django.conf import settings


def dynamic_ratelimit(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):

        # Get the user from the request
        user = request.user

        # Get user plan
        plan = user.plan

        # Filter matching plan dict from setting in basis of user's plan
        matching_plan_dict = [d for d in settings.USER_PLANS_LIST if d['id'] == plan][0]

        # Format rete limit string
        rate = f'{matching_plan_dict["rate"]}/{matching_plan_dict["rate_unit"]}'
        print(rate)
        # Apply the rate limit
        ratelimited_view = ratelimit(key='user', rate=rate, block=True)(view_func)
        return ratelimited_view(request, *args, **kwargs)

    return _wrapped_view



