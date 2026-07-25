"""
Test script to verify all API endpoints are properly defined
Run this after starting the Flask app
"""

import requests

BASE_URL = "http://localhost:5000"

# Test credentials
TEST_USER = {
    'email': 'admin@prioritypulse.com',
    'password': 'admin123'
}

def test_routes():
    print("=" * 60)
    print("Testing PriorityPulse API Endpoints")
    print("=" * 60)
    
    with requests.Session() as session:
        # Test 1: Login
        print("\n1. Testing Login...")
        try:
            response = session.get(f"{BASE_URL}/login")
            if response.status_code == 200:
                print("   ✓ Login page accessible")
                
                # Try to login
                login_data = {
                    'email': TEST_USER['email'],
                    'password': TEST_USER['password']
                }
                response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
                if response.status_code == 200:
                    print("   ✓ Login successful")
                else:
                    print("   ⚠ Login failed (may need valid credentials)")
            else:
                print("   ✗ Login page not accessible")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test 2: Check main routes exist
        routes_to_test = [
            ('/citizen-dashboard', 'Citizen Dashboard'),
            ('/officer-dashboard', 'Officer Dashboard'),
            ('/admin-dashboard', 'Admin Dashboard'),
            ('/complaints', 'Complaints Page'),
            ('/analytics', 'Analytics Page'),
            ('/map-view', 'Map View Page'),
            ('/reports', 'Reports Page'),
        ]
        
        print("\n2. Testing Main Routes...")
        for route, name in routes_to_test:
            try:
                response = session.get(f"{BASE_URL}{route}")
                if response.status_code in [200, 302]:
                    print(f"   ✓ {name} ({route}) - OK")
                else:
                    print(f"   ✗ {name} ({route}) - Status: {response.status_code}")
            except Exception as e:
                print(f"   ✗ {name} ({route}) - Error: {e}")
        
        # Test 3: API Endpoints (these require authentication)
        api_endpoints = [
            ('/get_priority_queue', 'GET', None),
            ('/get_analytics_data', 'GET', None),
            ('/get_clusters', 'GET', None),
            ('/get_heatmap', 'GET', None),
        ]
        
        print("\n3. Testing API Endpoints (require auth)...")
        for endpoint, method, data in api_endpoints:
            try:
                if method == 'GET':
                    response = session.get(f"{BASE_URL}{endpoint}")
                else:
                    response = session.post(f"{BASE_URL}{endpoint}", json=data)
                
                if response.status_code == 200:
                    json_response = response.json()
                    if json_response.get('success'):
                        print(f"   ✓ {endpoint} - Working")
                    else:
                        print(f"   ⚠ {endpoint} - Response: {json_response}")
                elif response.status_code == 302:
                    print(f"   ⚠ {endpoint} - Redirecting (likely needs auth)")
                else:
                    print(f"   ✗ {endpoint} - Status: {response.status_code}")
            except Exception as e:
                print(f"   ✗ {endpoint} - Error: {e}")
        
        # Test 4: Predict endpoint
        print("\n4. Testing Prediction Endpoint...")
        try:
            predict_data = {
                'complaint_text': 'Test complaint - water leak in downtown area',
                'location': 'Downtown'
            }
            response = session.post(f"{BASE_URL}/predict", json=predict_data)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✓ Prediction working - Severity: {result['prediction']['severity_score']}")
                else:
                    print(f"   ⚠ Prediction returned error: {result}")
            else:
                print(f"   ✗ Prediction failed - Status: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Prediction error: {e}")
        
        # Test 5: Submit complaint endpoint
        print("\n5. Testing Complaint Submission...")
        try:
            complaint_data = {
                'complaint_text': 'Test complaint submission',
                'location': 'Test Location'
            }
            response = session.post(f"{BASE_URL}/submit-complaint", json=complaint_data)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✓ Complaint submission working - ID: {result['complaint_id']}")
                else:
                    print(f"   ⚠ Submission returned error: {result}")
            else:
                print(f"   ✗ Submission failed - Status: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Submission error: {e}")
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)
    print("\nNote: Some endpoints may redirect to login if not authenticated.")
    print("This is expected behavior for protected routes.")

if __name__ == "__main__":
    try:
        test_routes()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("\nMake sure the Flask app is running on http://localhost:5000")
