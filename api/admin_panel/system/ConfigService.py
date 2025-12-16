from api.admin_panel.system.models import SystemConfiguration


class ConfigService:
    """Service for managing system configuration values."""

    @staticmethod
    def get_all_configs():
        """Retrieve all system configurations.

        Returns:
            QuerySet: All SystemConfiguration instances.
        """
        configs = SystemConfiguration.objects.all()
        return configs

    @staticmethod
    def get_config(key, default=None):
        """Get a configuration value by key with optional default.

        Args:
            key (str): Configuration key.
            default (any, optional): Default value if key not found.

        Returns:
            str: Configuration value.

        Raises:
            SystemConfiguration.DoesNotExist: If key not found and no default provided.
        """
        try:
            config = SystemConfiguration.objects.get(key=key)
            return config.value
        except SystemConfiguration.DoesNotExist:
            if default:
                return default
            else:
                raise SystemConfiguration.DoesNotExist

    @staticmethod
    def set_config(key, value):
        """Set a configuration value by key.

        Args:
            key (str): Configuration key.
            value (str): Value to set.

        Returns:
            SystemConfiguration: The configuration instance.
        """
        config, created = SystemConfiguration.objects.get_or_create(key=key)
        config.value = value
        config.save()
        return config

    @staticmethod
    def batch_set_configs(configs_dict):
        """Set multiple configuration values in batch.

        Args:
            configs_dict (dict): Dictionary of key-value pairs to set.

        Returns:
            dict: Results with 'results' (dict of success statuses) and 'errors' (dict of error messages).
        """
        results = {}
        errors = {}

        for key, value in configs_dict.items():
            try:
                config, created = SystemConfiguration.objects.get_or_create(key=key)
                config.value = value
                config.save()

                results[key] = "updated" if not created else "created"
            except Exception as e:
                errors[key] = str(e)

        return {"results": results, "errors": errors}
