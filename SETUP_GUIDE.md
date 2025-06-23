# Ayala Foundation Backend Setup Guide

## 🚀 Quick Start

### 1. **OpenAI API Integration**

Your backend now has intelligent database querying capabilities! Here's how to set it up:

#### Get OpenAI API Key:
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account and get your API key
3. Add to your environment variables:

```bash
# Create .env file in /back directory
cd back
touch .env

# Add this to your .env file:
OPENAI_API_KEY=your_openai_api_key_here
```

#### New AI-Powered Endpoints:

**🔍 Smart Company Search:**
```
GET /api/v1/companies/ai-search?query=Find tech companies in Almaty with websites
```

**🎯 AI Company Suggestions:**
```
GET /api/v1/companies/ai-suggestions?project_description=Education project for children&investment_amount=50000&region=Almaty
```

### 2. **Google OAuth for iOS App**

#### Backend Setup:

1. **Get Google OAuth Credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Google+ API
   - Create OAuth 2.0 credentials
   - Add to your .env:

```bash
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
```

2. **New Google Auth Endpoints:**
```
POST /api/v1/auth/google/verify  # Verify Google ID token from iOS
GET /api/v1/auth/google/config   # Get Google Client ID for iOS app
```

#### SwiftUI iOS App Setup:

1. **Install GoogleSignIn SDK:**
```swift
// In your Package.swift or Xcode: Add GoogleSignIn
dependencies: [
    .package(url: "https://github.com/google/GoogleSignIn-iOS", from: "7.0.0")
]
```

2. **Configure Google Sign-In:**
```swift
// In your App.swift
import GoogleSignIn

@main
struct YourApp: App {
    init() {
        // Configure Google Sign-In
        guard let path = Bundle.main.path(forResource: "GoogleService-Info", ofType: "plist"),
              let dict = NSDictionary(contentsOfFile: path),
              let clientId = dict["CLIENT_ID"] as? String else {
            fatalError("GoogleService-Info.plist not found")
        }
        
        GIDSignIn.sharedInstance.configuration = GIDConfiguration(clientID: clientId)
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .onOpenURL { url in
                    GIDSignIn.sharedInstance.handle(url)
                }
        }
    }
}
```

3. **Google Sign-In Implementation:**
```swift
// AuthService.swift
import GoogleSignIn

class AuthService: ObservableObject {
    @Published var user: User?
    @Published var isAuthenticated = false
    
    private let baseURL = "http://localhost:8000/api/v1"
    
    func signInWithGoogle() async {
        guard let presentingViewController = UIApplication.shared.windows.first?.rootViewController else {
            return
        }
        
        do {
            let result = try await GIDSignIn.sharedInstance.signIn(withPresenting: presentingViewController)
            let idToken = result.user.idToken?.tokenString
            
            // Send ID token to your backend
            await verifyGoogleToken(idToken: idToken)
        } catch {
            print("Google Sign-In error: \(error)")
        }
    }
    
    private func verifyGoogleToken(idToken: String?) async {
        guard let token = idToken else { return }
        
        let url = URL(string: "\(baseURL)/auth/google/verify")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["token": token]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            let response = try JSONDecoder().decode(AuthResponse.self, from: data)
            
            DispatchQueue.main.async {
                self.user = response.user
                self.isAuthenticated = true
                // Store access_token for API calls
                UserDefaults.standard.set(response.access_token, forKey: "access_token")
            }
        } catch {
            print("Token verification error: \(error)")
        }
    }
}

struct AuthResponse: Codable {
    let access_token: String
    let token_type: String
    let user: User
}

struct User: Codable {
    let id: String
    let email: String
    let full_name: String
    let is_verified: Bool
}
```

4. **AI-Powered Company Search in SwiftUI:**
```swift
// CompanyService.swift
class CompanyService: ObservableObject {
    @Published var companies: [Company] = []
    @Published var suggestions: [CompanySuggestion] = []
    
    private let baseURL = "http://localhost:8000/api/v1"
    
    func smartSearch(query: String) async {
        let accessToken = UserDefaults.standard.string(forKey: "access_token") ?? ""
        
        let url = URL(string: "\(baseURL)/companies/ai-search?query=\(query.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? "")")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            let companies = try JSONDecoder().decode([Company].self, from: data)
            
            DispatchQueue.main.async {
                self.companies = companies
            }
        } catch {
            print("Search error: \(error)")
        }
    }
    
    func getAISuggestions(projectDescription: String, investmentAmount: Double, region: String?) async {
        let accessToken = UserDefaults.standard.string(forKey: "access_token") ?? ""
        
        var urlComponents = URLComponents(string: "\(baseURL)/companies/ai-suggestions")!
        urlComponents.queryItems = [
            URLQueryItem(name: "project_description", value: projectDescription),
            URLQueryItem(name: "investment_amount", value: String(investmentAmount))
        ]
        if let region = region {
            urlComponents.queryItems?.append(URLQueryItem(name: "region", value: region))
        }
        
        var request = URLRequest(url: urlComponents.url!)
        request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            let response = try JSONDecoder().decode(SuggestionsResponse.self, from: data)
            
            DispatchQueue.main.async {
                self.suggestions = response.data
            }
        } catch {
            print("Suggestions error: \(error)")
        }
    }
}
```

### 3. **Complete Environment Configuration**

Create `/back/.env` file with:

```bash
# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_DB=ayala_foundation
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-0125-preview
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=1000

# Security
JWT_SECRET_KEY=your_jwt_secret_key_here
SECRET_KEY=your_app_secret_key_here

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
```

### 4. **Running Your Backend**

```bash
# Install new dependencies
cd back
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or using Docker
cd ..
docker-compose up api postgres redis
```

### 5. **Testing AI Features**

**Example API Calls:**

1. **Smart Search:**
```bash
curl -X GET "http://localhost:8000/api/v1/companies/ai-search?query=Find large tech companies in Almaty with good websites" \
  -H "Authorization: Bearer your_jwt_token"
```

2. **AI Suggestions:**
```bash
curl -X GET "http://localhost:8000/api/v1/companies/ai-suggestions?project_description=Educational program for underprivileged children&investment_amount=100000&region=Almaty" \
  -H "Authorization: Bearer your_jwt_token"
```

3. **Google Auth:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/google/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "google_id_token_from_ios_app"
  }'
```

## 🎯 What You Get

### AI-Powered Features:
- ✅ Natural language company search ("Find tech companies in Almaty")
- ✅ Intelligent sponsor matching based on project description
- ✅ AI-generated approach strategies for each potential sponsor
- ✅ Smart conversation system for fund profile completion

### Authentication:
- ✅ Google Sign-In for iOS app
- ✅ JWT token-based authentication
- ✅ Automatic user creation for Google users

### Ready for iOS:
- ✅ CORS configured for mobile app
- ✅ RESTful API endpoints
- ✅ Structured JSON responses
- ✅ Error handling

Your SwiftUI app can now intelligently search for companies and get AI-powered sponsorship recommendations! 🚀 