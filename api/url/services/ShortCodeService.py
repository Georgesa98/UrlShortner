import string
import random
from redis import Redis
from config import settings
from config.settings_utils import get_short_code_pool_size, get_short_code_length


class ShortCodeService:
    CHARS = string.ascii_letters + string.digits
    POOL_KEY = "shortcode:available_pool"
    MIN_POOL_SIZE = get_short_code_pool_size()
    CODE_LENGTH = get_short_code_length()

    def __init__(self):
        self.redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )

    def generate_code(self):
        return "".join(random.choices(self.CHARS, k=self.CODE_LENGTH))

    def get_code(self):
        code = self.redis_client.spop(self.POOL_KEY)
        current_size = self.redis_client.scard(self.POOL_KEY)
        if current_size == 0:
            self.refill_pool()
            return self.generate_code()
        if current_size < self.MIN_POOL_SIZE * 0.3:
            self.refill_pool()
        return code

    def refill_pool(self, target_size: int = None):
        if target_size is None:
            target_size = self.MIN_POOL_SIZE

        current_size = self.redis_client.scard(self.POOL_KEY)
        codes_to_generate = target_size - current_size
        if codes_to_generate <= 0:
            return 0
        batch_size = 1000
        generated = 0

        while generated < codes_to_generate:
            batch = [
                self.generate_code()
                for _ in range(min(batch_size, codes_to_generate - generated))
            ]
            self.redis_client.sadd(self.POOL_KEY, *batch)
            generated += len(batch)
        return generated
