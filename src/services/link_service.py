from string import ascii_letters, digits


class URLGenerator:
    def __init__(self):
        self.alphabet = ascii_letters + digits
        self.current = [0, 0, 0, 0, 0]

    def _generate_url(self):
        url = "".join(self.alphabet[i] for i in self.current)

        for i in range(4, -1, -1):
            self.current[i] += 1
            if self.current[i] < len(self.alphabet):
                break
            self.current[i] = 0
        else:
            raise StopIteration

        yield url

    def get_next_url(self):
        return next(self._generate_url())
