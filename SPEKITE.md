# SignBridge AI - API Specification

## Overview
AI-powered ASL (American Sign Language) to text and speech translation API.

## Authentication

### POST /api/auth/register
Register a new user account.
```json
{
  "name": "string",
  "email": "string",
  "password": "string"
}
```

### POST /api/auth/login
Authenticate and receive JWT token.
```json
{
  "email": "string",
  "password": "string"
}
```

### POST /api/auth/logout
Logout (client-side token removal).

### POST /api/auth/reset-password
Request password reset (placeholder).

## Translation

### POST /api/translate
Translate ASL gesture from webcam image. Requires Bearer token.
```json
{
  "imageData": "base64-encoded-png",
  "language": "English" // optional, defaults to English
}
```
Response:
```json
{
  "detectedGesture": "HELLO",
  "translatedText": "HELLO — Hello",
  "confidence": 0.92,
  "language": "English",
  "speechLang": "en-US",
  "record": { ... }
}
```

### GET /api/history
Get user's translation history. Requires Bearer token.

### DELETE /api/history/{id}
Delete a translation record. Requires Bearer token.

## Admin (requires admin role)

### GET /api/admin/users
List all users.

### GET /api/admin/analytics
Get analytics (total users, translations, active users).

### GET /api/admin/translations
List all translations.

## Supported Languages
English, Hindi, Telugu, Spanish, French, German, Chinese, Japanese, Arabic, Portuguese, Russian, Italian, Korean, Bengali, Tamil, Urdu

## Supported Gestures
HELLO, THANKS, YES, NO, PLEASE, SORRY, HELP, GOOD MORNING, GOOD NIGHT
