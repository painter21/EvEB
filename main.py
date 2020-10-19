from pathlib import Path

import numpy as np
print(int(np.random.default_rng().random() * 2.99 + 2))

current = Path(__file__).parent / 'assets' / 'config.txt'
current_cwd = Path().cwd()
print(current_cwd)


class Vector3d:
    def __init__(self, x, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        return self.x == other.x

    def __add__(self, other):
        return Vector3d(self.x + other.x, self.y + other.y, self.z + other.z)

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


vec_c = Vector3d(z=6, x=5)
print(vec_c)


vec_a = Vector3d(0, 10, 0)
vec_b = Vector3d(0, 0, 1)
print(vec_a == vec_b)
print(vec_a + vec_b)

class Bot:
    def __init__(self, x: str):
        self._x: int = x

    def get_x(self):
        return self._x


bot = Bot(6)

print(bot)
print(bot._x)

bot._x = 7
print(bot._x)


z = [5, 4, 3]
if unwrapped := z:
    print(unwrapped)
else:
    print("YOLO")