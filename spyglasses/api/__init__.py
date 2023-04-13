import pkgutil
import importlib
from flask import Blueprint

module_names = [module_name for _, module_name,
                _ in pkgutil.iter_modules(__path__)]

# api.bp is the blueprint for the most recent version of the API
most_recent_version = f'spyglasses.api.{module_names[-1]}'
default_api = importlib.import_module(most_recent_version)
bp = default_api.bp
