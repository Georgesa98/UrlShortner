import string
import random
from config.redis_utils import get_redis_client
from config.settings_utils import get_short_code_pool_size, get_short_code_length


class ShortCodeService:
    """Service for generating and managing short codes using Redis pool."""

    CHARS = string.ascii_letters + string.digits
    POOL_KEY = "shortcode:available_pool"
    MIN_POOL_SIZE = get_short_code_pool_size()
    CODE_LENGTH = get_short_code_length()

    def __init__(self):
        """Initialize the ShortCodeService with Redis client."""
        self.redis_client = get_redis_client()

    def generate_code(self):
        """Generate a random short code of configured length.

        Returns:
            str: A random short code.
        """
        return "".join(random.choices(self.CHARS, k=self.CODE_LENGTH))

    def get_code(self):
        """Retrieve a short code from the pool or generate new one.

        Returns:
            str: A unique short code.
        """
        code = self.redis_client.spop(self.POOL_KEY)
        current_size = self.redis_client.scard(self.POOL_KEY)
        if current_size == 0:
            self.refill_pool()
            return self.generate_code()
        if current_size < self.MIN_POOL_SIZE * 0.3:
            self.refill_pool()
        return code

    def refill_pool(self, target_size: int = None):
        """Refill the short code pool to the target size.

        Args:
            target_size (int, optional): Target pool size. Defaults to MIN_POOL_SIZE.

        Returns:
            int: Number of codes added to pool.
        """
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
