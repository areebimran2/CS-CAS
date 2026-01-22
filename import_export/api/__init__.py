from ninja import Router

from .import_templates.base import router as import_templates_base_router
from .imports.base import router as imports_base_router
from .exports.base import router as exports_base_router

import_templates_router = Router()
import_templates_router.add_router('', import_templates_base_router)

imports_router = Router()
imports_router.add_router('', imports_base_router)

exports_router = Router()
exports_router.add_router('', exports_base_router)