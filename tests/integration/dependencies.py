class DependencyOverrides:
    """Factory for dependency override"""
    def __init__(self, app):
        self.app = app
        self._overrides = {}

    def set(self, dependency, override):
        self._overrides[dependency] = self.app.dependency_overrides.get(dependency)
        self.app.dependency_overrides[dependency] = override

    def clear(self):
        for dependency, original in self._overrides.items():
            if original is None:
                self.app.dependency_overrides.pop(dependency, None)
            else:
                self.app.dependency_overrides[dependency] = original
        self._overrides.clear()
