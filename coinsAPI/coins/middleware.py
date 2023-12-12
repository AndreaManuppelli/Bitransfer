from .views import update_coins_rate
class StartupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.coins_update()
        
    def __call__(self, request):
        response = self.get_response(request)
        return response
    def coins_update(self):
        update_coins_rate()
        pass