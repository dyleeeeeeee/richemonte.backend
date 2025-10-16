#!/usr/bin/env python3
"""
Comprehensive Frontend-Backend Sync Audit
"""

from app import create_app
import re

def extract_frontend_endpoints():
    """Extract all API endpoints from frontend lib/api.ts"""
    endpoints = []

    # Read the frontend API file
    with open('c:/Users/User/Documents/Projects/sites/ilab/lib/api.ts', 'r') as f:
        content = f.read()

    # Find all fetchAPI calls
    pattern = r'fetchAPI<[^>]*>\s*\(\s*["\']([^"\']+)["\']'
    matches = re.findall(pattern, content)

    for endpoint in matches:
        endpoints.append(endpoint)

    return set(endpoints)

def extract_backend_routes():
    """Extract all registered backend routes"""
    app = create_app()
    routes = set()

    for rule in app.url_map.iter_rules():
        routes.add(rule.rule)

    return routes

def audit_sync():
    """Audit frontend-backend sync"""
    print("="*80)
    print("FRONTEND-BACKEND SYNC AUDIT")
    print("="*80)

    try:
        frontend_endpoints = extract_frontend_endpoints()
        backend_routes = extract_backend_routes()

        print(f"\nFrontend API endpoints found: {len(frontend_endpoints)}")
        print(f"Backend routes registered: {len(backend_routes)}")

        # Check for missing backend implementations
        missing_backends = frontend_endpoints - backend_routes
        if missing_backends:
            print(f"\n❌ MISSING BACKEND IMPLEMENTATIONS ({len(missing_backends)}):")
            for endpoint in sorted(missing_backends):
                print(f"   - {endpoint}")
        else:
            print("\n✅ All frontend endpoints have backend implementations")

        # Check for orphaned backend routes (routes that exist but aren't used by frontend)
        orphaned_routes = backend_routes - frontend_endpoints
        if orphaned_routes:
            print(f"\n⚠️  POTENTIALLY UNUSED BACKEND ROUTES ({len(orphaned_routes)}):")
            for route in sorted(orphaned_routes):
                if not route.startswith('/static') and not route.startswith('/_next'):
                    print(f"   - {route}")
        else:
            print("\n✅ No orphaned backend routes found")

        print("\n" + "="*80)
        print("AUDIT COMPLETE")
        print("="*80)

        return len(missing_backends) == 0

    except Exception as e:
        print(f"❌ AUDIT FAILED: {e}")
        return False

if __name__ == "__main__":
    success = audit_sync()
    exit(0 if success else 1)
