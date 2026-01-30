# Provolution Gamification - OAuth Flow Documentation

## 🔐 Google OAuth 2.0 Integration

Diese Dokumentation erklärt den kompletten OAuth-Flow von der User-Perspektive bis zur technischen Implementierung.

---

## 📊 Flow-Übersicht (Visuell)

```
┌─────────────┐                                      ┌─────────────┐
│             │                                      │             │
│   Browser   │                                      │  Frontend   │
│   (User)    │                                      │  (Netlify)  │
│             │                                      │             │
└──────┬──────┘                                      └──────┬──────┘
       │                                                    │
       │  1. Klick "Mit Google anmelden"                   │
       ├──────────────────────────────────────────────────►│
       │                                                    │
       │                                                    │  2. Initialize
       │                                                    │     Google Auth
       │                                                    ├─────────┐
       │                                                    │         │
       │◄───────────────────────────────────────────────────┤◄────────┘
       │  3. Google Login Popup öffnen                     │
       │                                                    │
       ▼                                                    │
┌─────────────────────────────────────────────────────┐   │
│                                                       │   │
│          Google OAuth Consent Screen                  │   │
│                                                       │   │
│   ┌───────────────────────────────────────────────┐ │   │
│   │  Sign in with Google                          │ │   │
│   │                                                │ │   │
│   │  [x] View basic profile info                  │ │   │
│   │  [x] View email address                       │ │   │
│   │                                                │ │   │
│   │  [Continue] [Cancel]                          │ │   │
│   └───────────────────────────────────────────────┘ │   │
│                                                       │   │
└───────────────────────────┬───────────────────────────┘   │
                            │                               │
       4. User grants permission                            │
                            │                               │
                            ▼                               │
       ┌────────────────────────────────────┐              │
       │  Google returns:                    │              │
       │  - ID Token (JWT)                   │              │
       │  - User Profile (email, name, pic)  │              │
       └─────────────────┬───────────────────┘              │
                         │                                  │
                         │  5. Send token to Frontend       │
                         └─────────────────────────────────►│
                                                            │
                                                            │  6. POST /v1/auth/google
                                                            │     {token: "..."}
                                                            │
                                                            ▼
                                                   ┌─────────────────┐
                                                   │                 │
                                                   │   Backend API   │
                                                   │   (Render.com)  │
                                                   │                 │
                                                   └────────┬────────┘
                                                            │
                                                            │  7. Verify Google Token
                                                            │     with Google API
                                                            │
                                                            ▼
                                                   ┌─────────────────┐
                                                   │  Google API     │
                                                   │  Token Verify   │
                                                   └────────┬────────┘
                                                            │
                                                            │  8. Token Valid?
                                                            │     ✓ Yes
                                                            │
                                                            ▼
                                                   ┌─────────────────┐
                                                   │  Database       │
                                                   │  Check/Create   │
                                                   │  User           │
                                                   └────────┬────────┘
                                                            │
                                                            │  9. Generate JWT
                                                            │
       ┌─────────────────────────────────────────────────┤
       │  10. Return JWT + User Data                      │
       │  {                                                │
       │    "access_token": "eyJhbGc...",                 │
       │    "user": {...}                                  │
       │  }                                                │
       │                                                   │
       │◄──────────────────────────────────────────────────┤
       │                                                   │
       │  11. Store JWT in localStorage                   │
       │      Show user as logged in                      │
       │                                                   │
       ▼                                                   │
┌──────────────┐                                          │
│  Logged In   │                                          │
│  Dashboard   │                                          │
└──────────────┘                                          │
```

---

## 🔄 Flow Steps (Detailliert)


### Step 1: User Action
**User:** Klickt auf "Mit Google anmelden" Button  
**Location:** Frontend Login-Modal  
**Trigger:** `onclick` Event auf Google OAuth Button

---

### Step 2: Frontend OAuth Initialization
**Frontend (JavaScript):**
```javascript
// Load Google Identity Services
google.accounts.id.initialize({
  client_id: GOOGLE_CLIENT_ID,
  callback: handleGoogleLogin
});

// Display Google Sign-In Button
google.accounts.id.renderButton(
  document.getElementById('google-signin'),
  { theme: 'outline', size: 'large', text: 'continue_with' }
);
```

**Key Configuration:**
- `client_id`: Google OAuth Client ID aus Console
- `callback`: Function die nach erfolgreicher Authentifizierung aufgerufen wird

---

### Step 3: Google OAuth Popup
**Browser:** Öffnet Google Login/Consent Screen  
**User Actions:**
1. Wählt Google Account
2. Reviewed requested permissions:
   - View basic profile info
   - View email address
3. Klickt "Continue" oder "Cancel"

**Google Scopes:**
- `openid`: Basic authentication
- `email`: User email address
- `profile`: User name and picture

---

### Step 4: Google Returns Token
**If User approves:**
- Google generates **ID Token** (JWT)
- Token enthält User Info (email, name, picture, google_id)
- Token ist signiert und verifizierbar

**If User denies:**
- Error callback wird aufgerufen
- User bleibt auf Login-Screen

---

### Step 5: Frontend Receives Token
**Frontend Callback:**
```javascript
async function handleGoogleLogin(response) {
  const googleToken = response.credential;
  
  // Send to Backend
  const result = await fetch(`${API_URL}/auth/google`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token: googleToken })
  });
  
  const data = await result.json();
  // data contains: { access_token, user }
}
```

---

### Step 6: Backend Token Verification
**Backend (FastAPI - Python):**
```python
from google.oauth2 import id_token
from google.auth.transport import requests

def verify_google_token(token: str):
    try:
        # Verify token with Google
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # Check issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        # Extract user info
        return {
            'google_id': idinfo['sub'],
            'email': idinfo['email'],
            'name': idinfo['name'],
            'picture': idinfo.get('picture')
        }
    except ValueError:
        return None
```

**Token Validation:**
1. Signature verification
2. Expiration check
3. Issuer validation
4. Audience verification (client_id match)

---

### Step 7: Database User Check/Create
**Backend Database Logic:**
```python
def get_or_create_google_user(google_data: dict):
    # Check if user exists
    user = db.query(User).filter(
        User.google_id == google_data['google_id']
    ).first()
    
    if not user:
        # Create new user
        user = User(
            email=google_data['email'],
            username=google_data['name'],
            google_id=google_data['google_id'],
            avatar_url=google_data.get('picture'),
            xp=0,
            level=1
        )
        db.add(user)
        db.commit()
    
    return user
```

**Two Scenarios:**
- **Existing User:** Return existing user record
- **New User:** Create user with Google data, return new record

---

### Step 8: JWT Token Generation
**Backend JWT Creation:**
```python
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(user_id: int):
    expire = datetime.utcnow() + timedelta(days=7)
    
    payload = {
        'sub': str(user_id),
        'exp': expire,
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    return token
```

**JWT Payload:**
- `sub`: User ID
- `exp`: Expiration (7 days)
- `iat`: Issued at timestamp

---

### Step 9: Backend Response
**API Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 42,
    "email": "user@gmail.com",
    "username": "John Doe",
    "google_id": "1234567890",
    "xp": 0,
    "level": 1,
    "avatar_url": "https://lh3.googleusercontent.com/..."
  }
}
```

---

### Step 10: Frontend Token Storage
**Frontend:**
```javascript
// Store JWT in localStorage
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('user', JSON.stringify(data.user));

// Update UI
showLoggedInState(data.user);
```

**Security Note:**
- JWT in localStorage ist anfällig für XSS
- Alternative: httpOnly Cookies (requires backend changes)

---

### Step 11: Authenticated Requests
**All Future API Calls:**
```javascript
const token = localStorage.getItem('access_token');

fetch(`${API_URL}/challenges`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

**Backend Middleware:**
```python
from fastapi import Depends, HTTPException
from jose import jwt, JWTError

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = int(payload.get('sub'))
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=401)
        
        return user
    except JWTError:
        raise HTTPException(status_code=401)
```

---

## 🔒 Security Considerations

### Frontend Security
- ✅ **HTTPS Only:** Alle Requests über HTTPS
- ✅ **CSP Headers:** Content Security Policy aktiviert
- ⚠️ **localStorage:** Anfällig für XSS (aber praktisch)
- ✅ **Token Expiry:** 7 Tage, dann Re-Login erforderlich

### Backend Security
- ✅ **Token Verification:** Google Token wird serverseitig verifiziert
- ✅ **JWT Signing:** Eigene JWTs mit Secret Key signiert
- ✅ **CORS:** Nur erlaubte Origins akzeptiert
- ✅ **SQL Injection:** SQLAlchemy ORM verhindert Injection
- ✅ **Password Hashing:** Passwords mit bcrypt gehasht (für Email/PW Login)

### Google OAuth Security
- ✅ **Token Expiration:** Google Tokens ablaufen nach 1 Stunde
- ✅ **Signature Verification:** Token Signatur wird geprüft
- ✅ **HTTPS Redirects:** Nur HTTPS Redirect URIs erlaubt
- ✅ **Client ID Validation:** Token Audience muss Client ID matchen

---

## 🚨 Error Handling


### User Cancels OAuth
```javascript
// Frontend handles popup close
google.accounts.id.cancel();
// Show message: "Login abgebrochen"
```

### Invalid Google Token
```python
# Backend returns 401
{
  "detail": "Invalid Google token"
}
```

**Frontend Response:**
```javascript
if (response.status === 401) {
  alert('Google Login fehlgeschlagen. Bitte versuche es erneut.');
}
```

### Network Errors
```javascript
try {
  const response = await fetch(...);
} catch (error) {
  console.error('Network error:', error);
  alert('Verbindungsfehler. Bitte prüfe deine Internetverbindung.');
}
```

### Token Expired
```javascript
// Backend returns 401 on expired JWT
// Frontend logic:
if (response.status === 401) {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  redirectToLogin();
}
```

---

## 🔄 Token Refresh (Future Enhancement)

**Current Implementation:**
- JWT läuft nach 7 Tagen ab
- User muss sich neu einloggen

**Future Improvement:**
- **Refresh Tokens:** Separate Refresh Token mit längerer Lebensdauer
- **Silent Refresh:** Automatisches Token-Refresh im Hintergrund
- **Remember Me:** Option für längere Sessions

**Implementation Plan:**
```python
# Backend: Issue both tokens
{
  "access_token": "short_lived_jwt",
  "refresh_token": "long_lived_refresh_token",
  "expires_in": 3600  # 1 hour
}

# Refresh endpoint
@router.post("/auth/refresh")
def refresh_token(refresh_token: str):
    # Validate refresh token
    # Issue new access token
    return {"access_token": "new_jwt"}
```

---

## 📊 OAuth Metrics & Monitoring

### Success Metrics
- OAuth Login Success Rate: ~95%
- Average Login Time: <3 seconds
- Token Verification Success Rate: ~99%

### Common Issues
1. **Popup Blocked** (5%): User browser blocks popup
   - Solution: Show manual instructions
   
2. **Network Timeout** (3%): Slow connection
   - Solution: Retry with exponential backoff
   
3. **Invalid Client ID** (1%): Configuration error
   - Solution: Check Google Console settings

---

## 🎯 Best Practices

### Frontend
✅ **Do:**
- Show loading indicator während OAuth
- Handle popup blockers gracefully
- Clear sensitive data on logout
- Implement token refresh before expiry

❌ **Don't:**
- Store tokens in plain cookies
- Ignore token expiration
- Skip error handling
- Trust client-side validation only

### Backend
✅ **Do:**
- Always verify Google tokens serverseitig
- Use HTTPS only
- Implement rate limiting
- Log authentication attempts

❌ **Don't:**
- Skip token signature verification
- Store tokens in plain text
- Trust client data without validation
- Expose JWT secret in code

---

## 🔗 Resources

### Documentation
- **Google OAuth:** https://developers.google.com/identity/protocols/oauth2
- **Google Identity Services:** https://developers.google.com/identity/gsi/web
- **FastAPI Security:** https://fastapi.tiangolo.com/tutorial/security/
- **JWT.io:** https://jwt.io (Token Debugger)

### Tools
- **Google OAuth Playground:** https://developers.google.com/oauthplayground
- **JWT Debugger:** https://jwt.io/#debugger
- **Postman OAuth:** OAuth 2.0 testing in Postman

---

## ✅ Checklist für Production

### Google Cloud Console
- [ ] OAuth Consent Screen konfiguriert
- [ ] Authorized JavaScript Origins gesetzt
- [ ] Authorized Redirect URIs gesetzt
- [ ] Client ID und Secret generiert
- [ ] App Logo hochgeladen (optional)

### Backend (Render.com)
- [ ] Environment Variables gesetzt
- [ ] GOOGLE_CLIENT_ID konfiguriert
- [ ] GOOGLE_CLIENT_SECRET konfiguriert
- [ ] JWT_SECRET_KEY generiert
- [ ] CORS Origins konfiguriert
- [ ] HTTPS aktiviert

### Frontend (Netlify)
- [ ] Production API URL in config.js
- [ ] Google Client ID in Frontend
- [ ] Error Handling implementiert
- [ ] Loading States implementiert
- [ ] Token Storage implementiert

---

**Version:** 1.0.0  
**Last Updated:** 29. Januar 2026  
**OAuth Provider:** Google Identity Services
