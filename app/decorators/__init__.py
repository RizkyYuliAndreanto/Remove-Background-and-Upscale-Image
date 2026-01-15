"""
Decorators Module
Kumpulan decorator untuk authorization, authentication, dan validation
"""

# PERBAIKAN: Ubah 'internal_service_required' menjadi 'internal_key_required'
from app.decorators.security import api_key_required, internal_key_required
from app.decorators.roles import admin_required, premium_required

__all__ = [
    'api_key_required',
    'internal_key_required',  # Update di sini juga
    'admin_required',
    'premium_required'
]