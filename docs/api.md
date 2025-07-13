# Aksjeradar API Documentation

## Overview
This document describes the Aksjeradar API endpoints, their usage, and expected responses.

## Authentication
Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:
```
Authorization: Bearer <your_token>
```

## Rate Limits
- General API endpoints: 200 requests per day, 50 per hour
- Login attempts: 5 per minute
- Password reset requests: 3 per minute
- Registration attempts: 3 per minute

## Endpoints

### Authentication

#### POST /login
Login to get access token.
```json
Request:
{
    "username": "string",
    "password": "string"
}

Response:
{
    "status": "OK",
    "message": "Welcome back, {username}!",
    "user": {
        "id": "integer",
        "username": "string",
        "subscription_type": "string",
        "has_active_subscription": "boolean"
    }
}
```

#### POST /register
Register a new user.
```json
Request:
{
    "username": "string",
    "email": "string",
    "password": "string"
}

Response:
{
    "status": "OK",
    "message": "Welcome, {username}! Your account has been created.",
    "user": {
        "id": "integer",
        "username": "string",
        "subscription_type": "string"
    }
}
```

### Subscription Management

#### GET /api/subscription/status
Get current user's subscription status.
```json
Response:
{
    "status": "OK",
    "subscription": {
        "active": "boolean",
        "type": "string",
        "start_date": "string (ISO format)",
        "end_date": "string (ISO format)",
        "days_remaining": "integer"
    }
}
```

#### POST /stripe/create-checkout-session
Create a new subscription checkout session.
```json
Request:
{
    "subscription_type": "string (monthly/yearly)"
}

Response:
{
    "status": "OK",
    "redirect_url": "string (Stripe checkout URL)"
}
```

### Portfolio Management

#### GET /portfolio
Get user's portfolio data.
```json
Response:
{
    "status": "OK",
    "portfolio_data": {
        "total_value": "number",
        "total_return": "number",
        "holdings": [
            {
                "symbol": "string",
                "shares": "integer",
                "value": "number"
            }
        ]
    }
}
```

### Stock Analysis

#### GET /analysis
Get stock analysis data.
```json
Response:
{
    "status": "OK",
    "analysis_types": ["string"],
    "premium_features": ["string"]
}
```

## Error Handling
All endpoints return errors in the following format:
```json
{
    "status": "ERROR",
    "message": "Error description",
    "code": "HTTP status code"
}
```

## Rate Limiting Headers
Each response includes rate limit headers:
```
X-RateLimit-Limit: Maximum requests allowed in the current period
X-RateLimit-Remaining: Number of requests remaining in the current period
X-RateLimit-Reset: Time when the rate limit will reset (UTC timestamp)
```
