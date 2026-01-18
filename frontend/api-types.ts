/**
 * API Types for URL Shortener Service
 * This file contains all request and response types for the API endpoints
 */

// ==================== URL Shortening API Types ====================

// Request Types
export interface CreateUrlRequest {
    long_url: string;
    short_url?: string; // Optional: Custom alias for the short URL
    expiry_date?: string; // Optional: Expiration date in ISO format
}

export interface BatchCreateUrlRequestItem {
    long_url: string;
    short_url?: string;
    expiry_date?: string;
}

export type BatchCreateUrlRequest = BatchCreateUrlRequestItem[];

export interface UpdateUrlRequest {
    long_url?: string;
    expiry_date?: string;
}

// Response type for single URL creation (same as UrlResponse)
export type CreateUrlResponse = UrlResponse;

// Response type for batch creation
export interface BatchCreateUrlResponse {
    // Array of created URL objects with the same structure as single URL creation
    urls: UrlResponse[];
}

export interface GetSpecificUrlPathParams {
    short_url: string; // The short URL identifier
}

export interface ListUrlsQueryParams {
    limit?: number; // Number of results per page (default: 10)
    page?: number; // Page number (default: 1)
    url_status?: string; // Filter by URL status (e.g., 'active', 'expired')
}

export interface UpdateUrlPathParams {
    short_url: string; // The short URL identifier
}

export interface DeleteUrlPathParams {
    short_url: string; // The short URL identifier
}

export interface GenerateQRCodePathParams {
    short_url: string; // The short URL identifier
}

// Response Types
export interface UrlResponse {
    id: number;
    name: string;
    long_url: string;
    short_url: string;
    user: number;
    expiry_date?: string;
    is_custom_alias: boolean;
    created_at: string;
    updated_at: string;
    visits: number;
    url_status: {
        state: string;
        reason: string | null;
    };
    last_accessed: string | null;
    days_until_expiry: number;
}

export interface ListUrlsResponse {
    urls: UrlResponse[];
    pagination: {
        total: number;
        page: number;
        limit: number;
        total_pages: number;
        has_next: boolean;
        has_previous: boolean;
    };
}

export interface RedirectResponse {
    // This is a redirect response, typically just a 302 status
}

export interface GenerateQRCodeResponse {
    // This returns a PNG image, so no specific type needed
}

// ==================== Redirection Rules API Types ====================

// Request Types
export interface ListRedirectionRulesQueryParams {
    url_id?: string; // Filter rules by URL ID
    is_active?: boolean; // Filter by active status (true/false)
}

export interface RedirectionRuleCondition {
    device_type?: string; // "mobile" or "desktop"
    country?: string[]; // Array of ISO 3166-1 alpha-2 country codes
    browser?: string; // Browser name (e.g., "chrome", "firefox", "safari")
    os?: string; // Operating system (e.g., "windows", "macos", "linux", "android", "ios")
    language?: string[]; // Array of ISO 639-1 language codes
    mobile?: boolean; // Boolean for mobile device detection
    referrer?: string[]; // Array of domain patterns (e.g., ["google.com"])
    time_range?: {
        start: string; // Start time in HH:MM format
        end: string; // End time in HH:MM format
    };
}

export interface CreateRedirectionRuleRequest {
    name: string;
    url_id: number;
    conditions: RedirectionRuleCondition;
    target_url: string;
    priority: number;
    is_active: boolean;
}

export interface BatchCreateRedirectionRulesRequest {
    rules: CreateRedirectionRuleRequest[];
}

export interface BatchDeleteRedirectionRulesRequest {
    rule_ids: number[];
}

export interface UpdateRedirectionRuleRequest {
    name?: string;
    url_id?: number;
    conditions?: RedirectionRuleCondition;
    target_url?: string;
    priority?: number;
    is_active?: boolean;
}

export interface GetRedirectionRulePathParams {
    id: string; // The redirection rule ID
}

export interface UpdateRedirectionRulePathParams {
    id: string; // The redirection rule ID
}

export interface DeleteRedirectionRulePathParams {
    id: string; // The redirection rule ID
}

export interface TestRedirectionRuleRequest {
    url_id: number;
    country?: string; // Optional: 2-letter ISO country code
    device_type?: string; // Optional: "mobile" | "desktop" | "tablet"
    browser?: string; // Optional: Browser name
    os?: string; // Optional: Operating system
    language?: string; // Optional: 2-letter language code
    mobile?: boolean; // Optional: Boolean for mobile device
    referrer?: string; // Optional: Referrer URL
    time_range?: string; // Optional: Current time in HH:MM format
}

// Response Types
export interface RedirectionRuleResponse {
    id: string;
    name: string;
    url: string;
    conditions: RedirectionRuleCondition;
    target_url: string;
    priority: number;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface ListRedirectionRulesResponse {
    success: boolean;
    message: string;
    data: RedirectionRuleResponse[];
}

export interface BatchCreateRedirectionRulesResponse {
    success: boolean;
    message: string;
    data: {
        created_rules: RedirectionRuleResponse[];
        failed_rules: any[]; // Array of failed rule details
    };
}

export interface BatchDeleteRedirectionRulesResponse {
    success: boolean;
    message: string;
    data: {
        deleted_count: number;
        failed_rules: any[]; // Array of failed rule details
    };
}

export interface GetRedirectionRuleResponse {
    success: boolean;
    message: string;
    data: RedirectionRuleResponse;
}

export interface UpdateRedirectionRuleResponse {
    success: boolean;
    message: string;
    data: RedirectionRuleResponse;
}

export interface DeleteRedirectionRuleResponse {
    success: boolean;
    message: string;
}

export interface TestRedirectionRuleResponse {
    success: boolean;
    message: string;
    data: {
        matched_rule: RedirectionRuleResponse;
        target_url: string;
        test_context: {
            device_type?: string;
            referrer?: string;
        };
    };
}

// ==================== Analytics API Types ====================

// Request Types
export interface GetUrlSummaryPathParams {
    url_id: number; // The URL ID
}

export interface GetUrlSummaryQueryParams {
    days?: number; // Number of days to analyze (default: 7)
}

// Response Types
export interface GetTopVisitedUrlsResponse {
    top_urls: UrlResponse[];
    count: number;
}

export interface DailyVisitResponse {
    date: string;
    daily_visits: number;
    unique_visits: number;
}

export interface UniqueVsTotalResponse {
    unique: number;
    total: number;
}

export interface TopMetricResponse {
    device?: string;
    browser?: string;
    operating_system?: string;
    geolocation?: string;
    count: number;
}

export interface GetUrlSummaryResponse {
    basic_info: {
        id: number;
        long_url: string;
        short_url: string;
        created_at: string;
        updated_at: string;
        visits: number;
        unique_visits: number;
        expiry_date?: string;
    };
    analytics: {
        daily_visits: DailyVisitResponse[];
        unique_vs_total: UniqueVsTotalResponse;
    };
    top_metrics: {
        devices: TopMetricResponse[];
        browsers: TopMetricResponse[];
        operating_systems: TopMetricResponse[];
        countries: TopMetricResponse[];
    };
    recent_visitors: any[]; // Array of recent visitor details
}

// ==================== Admin Panel API Types ====================

// Request Types
export interface GetUserUrlsQueryParams {
    limit?: number; // Number of results per page (default: 10)
    page?: number; // Page number (default: 1)
}

export interface GetUserUrlsPathParams {
    user_id: number; // The ID of the user whose URLs to retrieve
}

export interface BulkUrlDeletionRequest {
    url_ids: number[]; // Array of URL IDs to delete
}

export interface UpdateUrlDestinationRequest {
    new_destination: string;
}

export interface SearchUrlsQueryParams {
    query?: string; // Search term
    limit?: number;
    page?: number;
}

export interface BulkFlagUrlsRequest {
    url_ids: number[];
    reason: string;
}

export interface SearchUsersQueryParams {
    query?: string; // Search term (email, username)
    limit?: number;
    page?: number;
}

export interface ToggleBanUserRequest {
    banned: boolean;
    reason: string;
}

export interface UpdateUrlDestinationPathParams {
    short_url: string; // The short URL identifier
}

export interface GetUrlDetailsPathParams {
    url_id: number; // The ID of the URL
}

export interface GetUserDetailsPathParams {
    user_id: number; // The ID of the user
}

export interface ToggleBanUserPathParams {
    user_id: number; // The ID of the user
}

export interface BulkUserDeletionRequest {
    user_ids: number[];
}

// Response Types
export interface GetUserUrlsResponse {
    urls: UrlResponse[];
    pagination: {
        total: number;
        page: number;
        limit: number;
        total_pages: number;
        has_next: boolean;
        has_previous: boolean;
    };
}

export interface UpdateUrlDestinationResponse {
    // Response is an updated URL object (same as UrlResponse)
    id: number;
    long_url: string;
    short_url: string;
    user: number;
    expiry_date?: string;
    is_custom_alias: boolean;
    created_at: string;
    updated_at: string;
    visits: number;
    url_status: {
        state: string;
        reason: string | null;
    };
    last_accessed: string | null;
    days_until_expiry: number;
}

export interface GetUrlDetailsResponse {
    // Detailed URL object including status, creation info, etc.
    id: number;
    long_url: string;
    short_url: string;
    user: number;
    expiry_date?: string;
    is_custom_alias: boolean;
    created_at: string;
    updated_at: string;
    visits: number;
    url_status: {
        state: string;
        reason: string | null;
    };
    last_accessed: string | null;
    days_until_expiry: number;
}

export interface SearchUrlsResponse {
    // Paginated list of URLs matching the search criteria
    urls: UrlResponse[];
    pagination: {
        total: number;
        page: number;
        limit: number;
        total_pages: number;
        has_next: boolean;
        has_previous: boolean;
    };
}

export interface BulkFlagUrlsResponse {
    // Confirmation of flagged URLs
    success: boolean;
    message: string;
}

export interface GetUsersResponse {
    // Paginated list of users
    users: any[]; // User object structure not specified in docs
    pagination: {
        total: number;
        page: number;
        limit: number;
        total_pages: number;
        has_next: boolean;
        has_previous: boolean;
    };
}

export interface GetUserDetailsResponse {
    // Detailed user object
    // User object structure not specified in docs
}

export interface SearchUsersResponse {
    // Paginated list of users matching the search
    users: any[]; // User object structure not specified in docs
    pagination: {
        total: number;
        page: number;
        limit: number;
        total_pages: number;
        has_next: boolean;
        has_previous: boolean;
    };
}

export interface ToggleBanUserResponse {
    // Updated user status
    // User object structure not specified in docs
}

// Response type for bulk user deletion (204 No Content)
export type BulkUserDeletionResponse = void;

// ==================== System Health Monitoring API Types ====================

// Response Types
export interface HealthCheckResponse {
    status: "healthy" | "degraded" | "unhealthy"; // or "degraded" or "unhealthy"
    components: {
        database: {
            status: "healthy" | "degraded" | "unhealthy";
            latency_ms: number;
            vendor: string;
            database: string;
            host: string;
        };
        redis: {
            status: "healthy" | "degraded" | "unhealthy";
            latency_ms: number;
            host: string;
            port: number;
        };
        disk: {
            status: "healthy" | "degraded" | "unhealthy";
            total_gb: number;
            used_gb: number;
            free_gb: number;
            percent_used: number;
        };
        memory: {
            status: "healthy" | "degraded" | "unhealthy";
            total_gb: number;
            used_gb: number;
            free_gb: number;
            percent_used: number;
        };
        celery: {
            status: "healthy" | "degraded" | "unhealthy";
            latency_ms: number;
            broker_url: string;
            broker_connected: boolean;
            timezone: string;
        };
    };
}

// ==================== Platform Insights API Types ====================

// Request Types
export interface PlatformStatsQueryParams {
    time_range?: string; // Time range for statistics (e.g., '24h', '7d', '30d', default: '7d')
}

export interface GrowthMetricsQueryParams {
    growth_interval?: string; // Interval for growth metrics (e.g., 'daily', 'weekly', 'monthly', default: 'daily')
    data_points?: number; // Number of data points to return (default: 30)
    metrics?: string; // Comma-separated list of metrics to track (e.g., 'users_growth,urls_growth,clicks_volume', default: 'users_growth,urls_growth,clicks_volume')
}

export interface TopPerformersQueryParams {
    metric?: string; // Metric to rank by (e.g., 'visits', 'unique_visits', 'click_rate', default: 'visits')
    limit?: number; // Number of top performers to return (default: 10)
}

export interface PeakTimesQueryParams {
    time_range?: string; // Time range for analysis (e.g., '24h', '7d', '30d', default: '7d')
    granularity?: string; // Time granularity (e.g., 'hourly', 'daily', default: 'hourly')
}

export interface GeoDistQueryParams {
    time_range?: string; // Time range for analysis (e.g., '24h', '7d', '30d', default: '7d')
}

// Response Types
export interface PlatformStatsResponse {
    total_clicks: number;
    new_urls: number;
    new_users: number;
    new_visitors: number;
}

export interface GrowthMetricItem {
    date: string;
    new_users?: number;
    cumulative_users?: number;
    new_urls?: number;
    cumulative_urls?: number;
    clicks?: number;
}

export interface GrowthMetricsResponse {
    growth_interval: string;
    data_points: number;
    metrics: {
        users_growth?: GrowthMetricItem[];
        urls_growth?: GrowthMetricItem[];
        clicks_volume?: GrowthMetricItem[];
    };
}

export interface TopPerformerResponse {
    rank: number;
    identifier_type: string;
    identifier_value: string;
    metric: string;
    metric_value: number;
    details: {
        short_url: string;
        long_url: string;
    };
}

export interface TopPerformersResponse {
    top_performers: TopPerformerResponse[];
}

export interface PeakTimeResponse {
    time: string;
    visits: number;
}

export interface PeakTimesResponse {
    day: {
        peak_day: string;
        avg_clicks: number;
    };
    hour: {
        peak_hour: string;
        avg_clicks: number;
    };
}

export interface GeoDistItem {
    country: string;
    visits: number;
}

export interface GeoDistResponse {
    geo_distribution: GeoDistItem[];
}

// ==================== General API Types ====================

// Error Response Types
export interface ErrorResponse {
    error: string; // Error message describing the issue
}

export interface DetailErrorResponse {
    detail: string; // Error message
}

// ==================== Authentication API Types ====================

// Request Types
export interface LoginRequest {
    username: string;
    password: string;
}

// Response Types
export interface LoginResponse {
    // Response structure for JWT authentication with tokens in cookies
    // The actual tokens are stored in HTTP-only cookies
    // This response may contain user info or just be a confirmation
    success: boolean;
    message?: string;
    user?: {
        id: number;
        email: string;
        username?: string;
    };
}
export interface SignupRequest {
    email: string;
    username: string;
    password: string;
    rePassword: string;
    terms: boolean;
}

// ==================== System Configuration Management API Types ====================

// Request Types
export interface ListSystemConfigQueryParams {
    limit?: number;
    page?: number;
}

export interface GetSystemConfigPathParams {
    key: string; // The configuration key to retrieve
}

export interface SystemConfiguration {
    key: string;
    value: string;
    description?: string;
}

export interface BatchCreateSystemConfigRequest {
    configurations: SystemConfiguration[];
}

// Response Types
export interface ListSystemConfigResponse {
    configurations: SystemConfiguration[];
    pagination: {
        total: number;
        page: number;
        limit: number;
        total_pages: number;
        has_next: boolean;
        has_previous: boolean;
    };
}

export interface GetSystemConfigResponse {
    configuration: SystemConfiguration;
}

export interface BatchCreateSystemConfigResponse {
    success: boolean;
    message: string;
}

// ==================== Fraud Detection API Types ====================

// Request Types
export interface FraudOverviewQueryParams {
    days?: number; // Number of days to analyze (default: 7)
}

// Response Types
export interface FraudOverviewResponse {
    success: boolean;
    message: string;
    data: {
        total_incidents: number;
        incidents_by_type: {
            suspicious_user_agent?: number;
            burst_protection?: number;
            throttle_violation?: number;
        };
        incidents_by_severity: {
            low: number;
            medium: number;
            high: number;
        };
        recent_incidents: any[]; // Array of recent incident details
        risk_trends: any; // Risk trend data
    };
}

// ==================== Link Rot Detection API Types ====================

// Request Types
export interface CheckUrlHealthPathParams {
    url_id: number; // The ID of the URL to check
}

export interface CheckUrlHealthRequest {
    url_id: number; // The ID of the URL to check
}

export interface CheckBatchUrlHealthRequest {
    url_ids: number[]; // Array of URL IDs to check
}

// Response Types
export interface CheckUrlHealthResponse {
    success: boolean;
    message: string;
    data: {
        url_id: number;
        is_healthy: boolean;
        status_code?: number;
        last_checked: string;
        error_message?: string;
    };
}

export interface CheckBatchUrlHealthResponse {
    success: boolean;
    message: string;
    data: Array<{
        url_id: number;
        is_healthy: boolean;
        status_code?: number;
        last_checked: string;
        error_message?: string;
    }>;
}

// ==================== Audit Trail API Types ====================

// Request Types
export interface GetAuditLogsQueryParams {
    user_id?: number; // Filter logs by user ID
    action?: string; // Filter logs by action type (CREATE, UPDATE, DELETE, GET)
    date_from?: string; // Filter logs from date (format: YYYY-MM-DD)
    date_to?: string; // Filter logs to date (format: YYYY-MM-DD)
    page?: number; // Page number for pagination (default: 1)
    page_size?: number; // Number of items per page (default: 10)
    sort_by?: string; // Sort field (default: -timestamp for descending order)
}

// Response Types
export interface GetAuditLogsResponse {
    data: Array<{
        id: number;
        action: string;
        timestamp: string;
        user_id: number;
        user_email: string;
        content_type: string;
        content_id: string;
        ip_address: string;
        changes: any; // Object containing field changes
        successful: boolean;
    }>;
    pagination: {
        current_page: number;
        total_pages: number;
        total_items: number;
        has_next: boolean;
        has_previous: boolean;
    };
}
export interface Pagination {
    total: number;
    page: number;
    limit: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
}
