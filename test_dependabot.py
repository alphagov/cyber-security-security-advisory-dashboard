from cyber_dependabot import enable_all_dependabot
import config
import storage


settings = config.load()

if settings.aws_region:
    storage.set_region(config.get_value("aws_region"))

if settings.storage:
    storage_options = config.get_value("storage")
    storage.set_options(storage_options)

enable_all_dependabot()
