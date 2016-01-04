
class Context:

    def __init__(self):
        self._ctx = [{}]
        self._actx = self._ctx[-1]

    def new_scope():
        self._ctx.append({})
        self._actx = self._ctx[-1]

    def end_scope():
        self._ctx.pop()
        self._actx = self._ctx[-1]

    def lookup(self, name):
        for scope in reversed(self._ctx):
            if name in scope:
                return scope[name]
        return None

    def is_name_bound(self, name):
        return self.lookup(name) is not None

    def add_binding(self, name, binding):
        self._actx[name] = binding

    def pick_fresh_name(self, name):
        new_name = str(name).upper()
        while self.is_name_bound(new_name):
            new_name += "'"
        binding = TypeVar(new_name)
        self.add_binding(new_name, binding)
        return binding