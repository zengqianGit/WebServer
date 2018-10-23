from models import Model


class Session(Model):
    def __init__(self, form):
        super().__init__(form)
        self.session_id = form.get('session_id', '')
        self.username = form.get('username', '')
