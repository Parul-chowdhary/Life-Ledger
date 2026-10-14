"""
LifeLedger Web Presentation Package.
Exports the Flask web blueprint.
"""
from lifeledger_web.controllers.web_controller import web_bp

__all__ = ["web_bp"]
