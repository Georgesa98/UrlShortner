from api.admin_panel.system.models import SystemConfiguration


class ConfigService:
    @staticmethod
    def get_all_configs():
        configs = SystemConfiguration.objects.all()
        return configs

    @staticmethod
    def get_config(key, default=None):
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
        config, created = SystemConfiguration.objects.get_or_create(key=key)
        config.value = value
        config.save()
        return config

    @staticmethod
    def batch_set_configs(configs_dict):
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
