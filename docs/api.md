# API Documentation

This document provides comprehensive API documentation for the URL Shortener service, including authentication, endpoints, request/response formats, and examples.

## Base URL

**Development:** `http://localhost:8000/api`

**Production:** `https://your-domain.com/api`

## Authentication

### Method

**Cookie-based JWT Authentication**

All authenticated endpoints require a valid JWT token stored in an httpOnly cookie. Tokens are automatically included in requests by the browser.

### Getting a Token

**Endpoint:** `POST /api/auth/jwt/create/`

**Description:** Login and obtain JWT access/refresh tokens

**Request:**

```json
{
  "username": "user@example.com",
  "password": "yourpassword123"
}
```

**Response (200 OK):**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Cookies set:**

- `access_token` - httpOnly, secure, 15-minute expiry
- `refresh_token` - httpOnly, secure, 7-day expiry

### Using Authentication

For browser-based clients, cookies are automatically included. For API clients:

```bash
# Login and save cookies
curl -X POST http://localhost:8000/api/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "pass123"}' \
  -c cookies.txt

# Use cookies in subsequent requests
curl -X POST http://localhost:8000/api/url/shorten/ \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://example.com", "name": "Example"}' \
  -b cookies.txt
```

### Logout

**Endpoint:** `POST /api/auth/logout/`

**Description:** Invalidate JWT tokens

**Response (200 OK):**

```json
{
  "message": "Successfully logged out"
}
```

## URL Management Endpoints

### Create Short URL

**Endpoint:** `POST /api/url/shorten/`

**Authentication:** Required

**Description:** Create a new shortened URL with optional custom alias and expiry date

**Request Body:**

```json
{
  "long_url": "https://example.com/very/long/url/path",
  "name": "Example Link",
  "short_url": "mylink",
  "expiry_date": "2024-12-31T23:59:59Z"
}
```

**Field Descriptions:**

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| long_url | string | Yes | Target URL to redirect to | Valid URL, max 2000 chars |
| name | string | Yes | User-friendly label | Max 512 chars |
| short_url | string | No | Custom alias (auto-generated if omitted) | 8-64 chars, alphanumeric + `-_`, must be unique |
| expiry_date | datetime | No | Optional expiration (ISO 8601) | Must be future date |

**Response (201 Created):**

```json
{
  "data": {
    "id": 123,
    "short_url": "mylink",
    "long_url": "https://example.com/very/long/url/path",
    "name": "Example Link",
    "user": 5,
    "is_custom_alias": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "expiry_date": "2024-12-31T23:59:59Z",
    "last_accessed": null,
    "visits": 0,
    "days_until_expiry": 350,
    "url_status": {
      "id": 123,
      "state": "ACTIVE",
      "reason": null,
      "last_checked": null
    }
  },
  "message": "URL shortened successfully"
}
```

**Error Responses:**

```json
// 400 Bad Request - Invalid URL
{
  "message": "please enter a valid url"
}

// 400 Bad Request - Alias taken
{
  "message": "custom alias already in use"
}

// 400 Bad Request - Invalid alias format
{
  "message": "custom alias can only contain letters, numbers, hyphens, and underscores"
}

// 429 Too Many Requests - Rate limit exceeded
{
  "message": "Request was throttled. Expected available in 3600 seconds."
}
```

**Rate Limits:**

- **Anonymous:** Not allowed
- **Authenticated users:** 100 requests/hour
- **IP-based:** 200 requests/hour

### Batch Create Short URLs

**Endpoint:** `POST /api/url/batch-shorten/`

**Authentication:** Required

**Description:** Create multiple shortened URLs in a single request (max 500)

**Request Body:**

```json
[
  {
    "long_url": "https://example.com/page1",
    "name": "Page 1",
    "short_url": "page1"
  },
  {
    "long_url": "https://example.com/page2",
    "name": "Page 2"
  },
  {
    "long_url": "https://example.com/page3",
    "name": "Page 3",
    "expiry_date": "2024-12-31T23:59:59Z"
  }
]
```

**Response (201 Created):**

```json
{
  "data": [
    {
      "id": 124,
      "short_url": "page1",
      "long_url": "https://example.com/page1",
      "name": "Page 1",
      "is_custom_alias": true,
      "created_at": "2024-01-15T10:30:00Z",
      "visits": 0,
      "url_status": {
        "state": "ACTIVE"
      }
    },
    {
      "id": 125,
      "short_url": "aB3xY9",
      "long_url": "https://example.com/page2",
      "name": "Page 2",
      "is_custom_alias": false,
      "created_at": "2024-01-15T10:30:01Z",
      "visits": 0,
      "url_status": {
        "state": "ACTIVE"
      }
    }
  ],
  "message": "URLs shortened successfully"
}
```

**Validation:**

- Maximum 500 URLs per request
- Each URL validated independently
- Failed URLs are skipped (partial success allowed)

### List URLs

**Endpoint:** `GET /api/url/`

**Authentication:** Required

**Description:** List all URLs owned by the authenticated user with pagination and filtering

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | integer | 10 | Results per page (1-100) |
| page | integer | 1 | Page number |
| url_status | string | - | Filter by state: ACTIVE, EXPIRED, FLAGGED, DISABLED, BROKEN |
| date_order | string | - | Sort by date: ASC or DESC |
| query | string | - | Search in long_url, short_url, or name |

**Example Request:**

```bash
GET /api/url/?limit=20&page=1&url_status=ACTIVE&date_order=DESC&query=example
```

**Response (200 OK):**

```json
{
  "data": {
    "urls": [
      {
        "id": 123,
        "short_url": "mylink",
        "long_url": "https://example.com/page",
        "name": "Example Link",
        "visits": 1247,
        "created_at": "2024-01-15T10:30:00Z",
        "url_status": {
          "state": "ACTIVE"
        }
      }
    ],
    "pagination": {
      "total": 45,
      "page": 1,
      "limit": 20,
      "total_pages": 3,
      "has_next": true,
      "has_previous": false
    }
  },
  "message": "URLs fetched successfully"
}
```

### Get Specific URL

**Endpoint:** `GET /api/url/{short_url}/`

**Authentication:** Required (must be owner)

**Description:** Retrieve details for a specific URL

**Response (200 OK):**

```json
{
  "data": {
    "id": 123,
    "short_url": "mylink",
    "long_url": "https://example.com/page",
    "name": "Example Link",
    "user": 5,
    "is_custom_alias": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "expiry_date": "2024-12-31T23:59:59Z",
    "last_accessed": "2024-01-15T15:45:00Z",
    "visits": 1247,
    "days_until_expiry": 350,
    "url_status": {
      "id": 123,
      "state": "ACTIVE",
      "reason": null,
      "last_checked": null
    }
  },
  "message": "URL retrieved successfully"
}
```

**Error Responses:**

```json
// 404 Not Found
{
  "message": "URL not found"
}

// 403 Forbidden - Not owner
{
  "message": "You do not have permission to perform this action."
}
```

### Update URL

**Endpoint:** `PATCH /api/url/{short_url}/`

**Authentication:** Required (must be owner)

**Description:** Update long_url or expiry_date (short_url cannot be changed)

**Request Body:**

```json
{
  "long_url": "https://example.com/new-target",
  "expiry_date": "2025-12-31T23:59:59Z"
}
```

**Response (200 OK):**

```json
{
  "data": {
    "id": 123,
    "short_url": "mylink",
    "long_url": "https://example.com/new-target",
    "expiry_date": "2025-12-31T23:59:59Z",
    "updated_at": "2024-01-15T16:00:00Z"
  },
  "message": "URL updated successfully"
}
```

### Delete URL

**Endpoint:** `DELETE /api/url/{short_url}/`

**Authentication:** Required (must be owner)

**Description:** Permanently delete a URL

**Response (204 No Content):**

```json
{
  "message": "URL deleted successfully"
}
```

### Redirect (Public Endpoint)

**Endpoint:** `GET /api/url/redirect/{short_url}/`

**Authentication:** Not required

**Description:** Redirect to the target URL (with analytics tracking and burst protection)

**Flow:**

1. Burst protection check (blocks if exceeded)
2. URL status validation (404 if expired/disabled)
3. Redirection rule evaluation (priority-based)
4. Analytics recording (buffered to Redis)
5. HTTP 302 redirect

**Response (302 Found):**

```
Location: https://example.com/target-page
```

**Error Responses:**

```json
// 404 Not Found
{
  "message": "URL not found"
}

// 410 Gone - Expired or disabled
{
  "message": "URL is inactive or expired"
}

// 429 Too Many Requests - Burst protection triggered
{
  "message": "Too many requests on this URL"
}
```

**Analytics Tracking:**

- IP address (hashed with SHA-256)
- Geolocation (country code)
- Browser, OS, device type
- Referrer
- Timestamp
- Unique visitor detection

### Generate QR Code

**Endpoint:** `GET /api/url/qr/{short_url}/`

**Authentication:** Required (must be owner)

**Description:** Generate a QR code PNG image for the short URL

**Response (200 OK):**

```
Content-Type: image/png

[Binary PNG data]
```

**Usage Example:**

```html
<!-- In HTML -->
<img src="http://localhost:8000/api/url/qr/mylink/" alt="QR Code" />
```

## Analytics Endpoints

### Get URL Summary

**Endpoint:** `GET /api/analytics/url-summary/{url_id}`

**Authentication:** Required (must be owner)

**Description:** Get detailed analytics for a specific URL

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| range_days | integer | 7 | Number of days to analyze (1-365) |

**Response (200 OK):**

```json
{
  "data": {
    "basic_info": {
      "id": 123,
      "long_url": "https://example.com/page",
      "short_url": "mylink",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "visits": 1247,
      "unique_visits": 892,
      "expiry_date": "2024-12-31T23:59:59Z",
      "url_status": {
        "state": "ACTIVE",
        "reason": null
      }
    },
    "analytics": {
      "daily_visits": [
        {
          "date": "2024-01-15",
          "daily_visits": 45,
          "unique_visits": 32
        },
        {
          "date": "2024-01-16",
          "daily_visits": 67,
          "unique_visits": 48
        }
      ],
      "unique_vs_total": {
        "unique": 892,
        "total": 1247
      }
    },
    "top_metrics": {
      "devices": [
        {"device": "Desktop", "count": 567},
        {"device": "Mobile", "count": 423},
        {"device": "Tablet", "count": 257}
      ],
      "browsers": [
        {"browser": "Chrome", "count": 678},
        {"browser": "Firefox", "count": 312},
        {"browser": "Safari", "count": 257}
      ],
      "operating_systems": [
        {"operating_system": "Windows", "count": 523},
        {"operating_system": "macOS", "count": 412},
        {"operating_system": "Linux", "count": 312}
      ],
      "countries": [
        {"geolocation": "US", "count": 567},
        {"geolocation": "GB", "count": 234},
        {"geolocation": "CA", "count": 189}
      ]
    },
    "recent_visitors": [
      {
        "id": 5001,
        "timestamp": "2024-01-15T15:45:00Z",
        "geolocation": "US",
        "browser": "Chrome",
        "operating_system": "Windows",
        "device": "Desktop",
        "referer": "https://google.com",
        "new_visitor": true
      }
    ]
  },
  "message": "Analytics retrieved successfully"
}
```

### Get User Stats

**Endpoint:** `GET /api/analytics/user-stats/`

**Authentication:** Required

**Description:** Get aggregate statistics for the authenticated user

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| range_days | integer | 7 | Number of days to analyze |

**Response (200 OK):**

```json
{
  "data": {
    "total_clicks": 5432,
    "active_links": 23,
    "top_referrer": {
      "referer": "https://google.com",
      "count": 1234
    }
  },
  "message": "User stats retrieved successfully"
}
```

### Get Top Visited URLs

**Endpoint:** `GET /api/analytics/top-visited/`

**Authentication:** Required

**Description:** Get the user's most visited URLs

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| num | integer | 10 | Number of top URLs to return (1-100) |

**Response (200 OK):**

```json
{
  "data": [
    {
      "id": 123,
      "short_url": "popular1",
      "long_url": "https://example.com/page1",
      "name": "Popular Page",
      "visits": 5432,
      "unique_visits": 3210,
      "url_status": {
        "state": "ACTIVE"
      }
    },
    {
      "id": 124,
      "short_url": "popular2",
      "long_url": "https://example.com/page2",
      "name": "Another Popular Page",
      "visits": 4321,
      "unique_visits": 2890,
      "url_status": {
        "state": "ACTIVE"
      }
    }
  ],
  "message": "Top URLs retrieved successfully"
}
```

## Redirection Rules Endpoints

### List Redirection Rules

**Endpoint:** `GET /api/url/redirection/rules/`

**Authentication:** Required

**Description:** List all redirection rules for user's URLs

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| url_id | integer | Filter by specific URL |

**Response (200 OK):**

```json
{
  "data": [
    {
      "id": 1,
      "url": 123,
      "name": "Mobile Users Redirect",
      "conditions": {
        "device_type": ["mobile"],
        "country": ["US", "CA"]
      },
      "target_url": "https://m.example.com/page",
      "priority": 10,
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "message": "Redirection rules retrieved successfully"
}
```

### Create Redirection Rule

**Endpoint:** `POST /api/url/redirection/rules/`

**Authentication:** Required (must own URL)

**Request Body:**

```json
{
  "url": 123,
  "name": "US Mobile Redirect",
  "conditions": {
    "country": ["US"],
    "device_type": ["mobile", "tablet"]
  },
  "target_url": "https://m.example.com/special",
  "priority": 10,
  "is_active": true
}
```

**Supported Condition Keys:**

- `country` - Array of ISO 3166-1 alpha-2 country codes
- `device_type` - Array: `["mobile", "tablet", "desktop"]`
- `browser` - Array: `["Chrome", "Firefox", "Safari", "Edge"]`
- `os` - Array: `["Windows", "macOS", "Linux", "iOS", "Android"]`
- `language` - Array of ISO 639-1 language codes
- `time_range` - Object: `{"start": "09:00", "end": "17:00", "timezone": "America/New_York"}`
- `mobile` - Boolean
- `referer` - Array of domain patterns

**Response (201 Created):**

```json
{
  "data": {
    "id": 2,
    "url": 123,
    "name": "US Mobile Redirect",
    "conditions": {
      "country": ["US"],
      "device_type": ["mobile", "tablet"]
    },
    "target_url": "https://m.example.com/special",
    "priority": 10,
    "is_active": true,
    "created_at": "2024-01-15T11:00:00Z",
    "updated_at": "2024-01-15T11:00:00Z"
  },
  "message": "Redirection rule created successfully"
}
```

### Update Redirection Rule

**Endpoint:** `PATCH /api/url/redirection/rules/{rule_id}/`

**Authentication:** Required (must own URL)

**Request Body:**

```json
{
  "is_active": false,
  "priority": 5
}
```

### Delete Redirection Rule

**Endpoint:** `DELETE /api/url/redirection/rules/{rule_id}/`

**Authentication:** Required (must own URL)

**Response (204 No Content)**

### Test Redirection Rule

**Endpoint:** `POST /api/url/redirection/rules/test/`

**Authentication:** Required

**Description:** Test which rule would match given conditions (without creating a visit)

**Request Body:**

```json
{
  "url_id": 123,
  "conditions": {
    "country": "US",
    "device_type": "mobile",
    "browser": "Chrome"
  }
}
```

**Response (200 OK):**

```json
{
  "data": {
    "matched_rule": {
      "id": 2,
      "name": "US Mobile Redirect",
      "target_url": "https://m.example.com/special",
      "priority": 10
    },
    "fallback_url": "https://example.com/page"
  },
  "message": "Rule test completed"
}
```

## Link Health Check Endpoints

### Check Single URL Health

**Endpoint:** `GET /api/link-rot/check-url-health/{url_id}/`

**Authentication:** Required (must own URL)

**Description:** Check if the target URL is accessible

**Response (200 OK):**

```json
{
  "data": {
    "url_id": 123,
    "status": "ACTIVE",
    "http_status": 200,
    "response_time_ms": 342,
    "last_checked": "2024-01-15T12:00:00Z"
  },
  "message": "Health check completed"
}
```

**Possible statuses:**

- `ACTIVE` - URL is accessible (HTTP 2xx/3xx)
- `BROKEN` - URL returns error (HTTP 4xx/5xx)
- `BROKEN` - Connection timeout/refused

### Batch Health Check

**Endpoint:** `POST /api/link-rot/check-batch-health/`

**Authentication:** Required

**Description:** Check health of multiple URLs (max 100)

**Request Body:**

```json
{
  "url_ids": [123, 124, 125]
}
```

**Response (200 OK):**

```json
{
  "data": {
    "results": [
      {
        "url_id": 123,
        "status": "ACTIVE",
        "http_status": 200
      },
      {
        "url_id": 124,
        "status": "BROKEN",
        "error": "404 Not Found"
      },
      {
        "url_id": 125,
        "status": "ACTIVE",
        "http_status": 301
      }
    ],
    "summary": {
      "total": 3,
      "active": 2,
      "broken": 1
    }
  },
  "message": "Batch health check completed"
}
```

## Rate Limiting

### IP-Based Throttling

**Limits:**

- **Anonymous requests:** 200 requests/hour
- **Authenticated requests:** Higher limits per endpoint

### User-Based Throttling

**Limits:**

- **URL creation:** 100/hour
- **Analytics queries:** 1000/hour
- **Redirect:** Unlimited (subject to burst protection)

### Burst Protection

**Limits (per IP or per URL):**

- **Short-term:** 10 requests / 10 seconds
- **Medium-term:** 50 requests / 60 seconds
- **Long-term:** 1000 requests / 3600 seconds

**Response when blocked:**

```json
{
  "message": "Too many requests on this URL"
}
```

## Error Responses

### Standard Error Format

```json
{
  "message": "Error description",
  "errors": {
    "field_name": ["Error message for this field"]
  }
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Resource deleted successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Permission denied |
| 404 | Not Found | Resource not found |
| 410 | Gone | Resource expired or disabled |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

## OpenAPI Schema

**Full API schema:** `GET /schema/`

**Interactive documentation:** `GET /docs/`

The system uses `drf-spectacular` to auto-generate OpenAPI 3.0 schema from Django REST Framework serializers and viewsets.

## Code Examples

### Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Login
response = requests.post(f"{BASE_URL}/auth/jwt/create/", json={
    "username": "user@example.com",
    "password": "password123"
})
cookies = response.cookies

# Create short URL
response = requests.post(f"{BASE_URL}/url/shorten/", json={
    "long_url": "https://example.com/page",
    "name": "Example"
}, cookies=cookies)

data = response.json()
short_url = data["data"]["short_url"]
print(f"Short URL: {short_url}")

# Get analytics
response = requests.get(
    f"{BASE_URL}/analytics/url-summary/{data['data']['id']}",
    params={"range_days": 30},
    cookies=cookies
)
analytics = response.json()
print(f"Total visits: {analytics['data']['basic_info']['visits']}")
```

### JavaScript (fetch)

```javascript
const BASE_URL = 'http://localhost:8000/api';

// Login
const login = async () => {
  const response = await fetch(`${BASE_URL}/auth/jwt/create/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: 'user@example.com',
      password: 'password123'
    }),
    credentials: 'include' // Important for cookies
  });
  return response.json();
};

// Create short URL
const createShortUrl = async (longUrl, name) => {
  const response = await fetch(`${BASE_URL}/url/shorten/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ long_url: longUrl, name: name }),
    credentials: 'include'
  });
  return response.json();
};

// Usage
await login();
const result = await createShortUrl('https://example.com', 'Example');
console.log(`Short URL: ${result.data.short_url}`);
```

### cURL

```bash
# Login and save cookies
curl -X POST http://localhost:8000/api/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user@example.com","password":"password123"}' \
  -c cookies.txt

# Create short URL
curl -X POST http://localhost:8000/api/url/shorten/ \
  -H "Content-Type: application/json" \
  -d '{"long_url":"https://example.com","name":"Example"}' \
  -b cookies.txt

# Get URL list
curl -X GET "http://localhost:8000/api/url/?limit=10&page=1" \
  -b cookies.txt

# Get analytics
curl -X GET "http://localhost:8000/api/analytics/url-summary/123?range_days=7" \
  -b cookies.txt
```

---

**Related Documentation:**

- [Architecture Overview](architecture.md)
- [Database Design](database.md)
- [Design Decisions](design-decisions.md)
- [Analytics Deep-Dive](deep-dive-analytics.md)
