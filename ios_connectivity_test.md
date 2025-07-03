# iOS App Connectivity Fix

## ✅ Backend Status
- **Server Running**: ✅ YES
- **Your Computer IP**: `192.168.58.253`
- **Backend Port**: `8000`
- **Test URL**: http://192.168.58.253:8000/health

## 📱 Step 1: Test from iPhone Safari

Open Safari on your iPhone and visit these URLs:

1. **Health Check**: 
   ```
   http://192.168.58.253:8000/health
   ```
   Should return: `{"status":"success","message":"API is healthy"...}`

2. **API Documentation**:
   ```
   http://192.168.58.253:8000/docs
   ```
   Should show the Swagger UI interface

## 🔧 Step 2: Update iOS App Code

### Fix 1: Update Base URL (CRITICAL)

In your iOS app, find where you define the API base URL and change it:

```swift
// ❌ OLD - This won't work on real iPhone
let baseURL = "http://localhost:8000"
let baseURL = "http://127.0.0.1:8000"

// ✅ NEW - Use your computer's actual IP
let baseURL = "http://192.168.58.253:8000"
```

### Fix 2: Add Proper Async Network Calls

Replace any blocking network calls with async versions:

```swift
// ❌ OLD - Blocks UI thread
func fetchData() {
    let url = URL(string: "\(baseURL)/api/v1/funds/profile")!
    let data = try! Data(contentsOf: url)  // This blocks!
}

// ✅ NEW - Async with proper error handling
func fetchData() async {
    guard let url = URL(string: "\(baseURL)/api/v1/funds/profile") else { return }
    
    do {
        let (data, response) = try await URLSession.shared.data(from: url)
        
        // Update UI on main thread
        await MainActor.run {
            // Handle successful response
            print("Data received: \(data)")
        }
    } catch {
        await MainActor.run {
            // Handle error
            print("Network error: \(error)")
        }
    }
}
```

### Fix 3: Add Network Timeouts

```swift
var request = URLRequest(url: url)
request.timeoutInterval = 10.0  // 10 second timeout
request.setValue("application/json", forHTTPHeaderField: "Content-Type")

// For authenticated requests
if let token = authToken {
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
}
```

### Fix 4: Test Authentication Flow

```swift
// Test login endpoint
func testLogin() async {
    let url = URL(string: "\(baseURL)/api/v1/auth/token")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
    
    let body = "username=test@demo.kz&password=testpassword"
    request.httpBody = body.data(using: .utf8)
    
    do {
        let (data, _) = try await URLSession.shared.data(for: request)
        let response = try JSONDecoder().decode(AuthResponse.self, from: data)
        print("Login successful: \(response.access_token)")
    } catch {
        print("Login failed: \(error)")
    }
}
```

## 🔍 Step 3: Debug Network Issues

If your app is still unresponsive:

1. **Check Network Permissions**: Ensure your app has network permissions
2. **Check ATS Settings**: Add this to Info.plist if using HTTP:
   ```xml
   <key>NSAppTransportSecurity</key>
   <dict>
       <key>NSAllowsArbitraryLoads</key>
       <true/>
   </dict>
   ```
3. **Add Network Logging**: 
   ```swift
   URLSession.shared.configuration.requestCachePolicy = .reloadIgnoringLocalCacheData
   ```

## 🎯 Quick Test

Add this simple test function to your iOS app:

```swift
func testBackendConnection() async {
    let url = URL(string: "http://192.168.58.253:8000/health")!
    
    do {
        let (data, _) = try await URLSession.shared.data(from: url)
        let json = try JSONSerialization.jsonObject(with: data)
        print("✅ Backend connection successful: \(json)")
    } catch {
        print("❌ Backend connection failed: \(error)")
    }
}
```

Call this function when your app starts to verify connectivity.

## 📞 Available Endpoints

Your backend has these endpoints available:

- `GET /health` - Health check
- `POST /api/v1/auth/token` - Login
- `POST /api/v1/auth/register` - Register
- `GET /api/v1/funds/profile` - Get fund profile
- `POST /api/v1/funds/chat` - AI conversation
- `GET /api/v1/companies/search` - Search companies

All endpoints require `http://192.168.58.253:8000` as the base URL when testing on your iPhone. 