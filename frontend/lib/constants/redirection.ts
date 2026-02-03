import countries from "world-countries";

// Country data with flags using world-countries package
export const COUNTRIES = countries
    .map((country) => ({
        code: country.cca2,
        name: country.name.common,
        flag: country.flag,
    }))
    .sort((a, b) => a.name.localeCompare(b.name));

// Popular countries for quick access
export const POPULAR_COUNTRIES = [
    { code: "US", name: "United States", flag: "🇺🇸" },
    { code: "GB", name: "United Kingdom", flag: "🇬🇧" },
    { code: "CA", name: "Canada", flag: "🇨🇦" },
    { code: "AU", name: "Australia", flag: "🇦🇺" },
    { code: "DE", name: "Germany", flag: "🇩🇪" },
    { code: "FR", name: "France", flag: "🇫🇷" },
    { code: "IN", name: "India", flag: "🇮🇳" },
    { code: "JP", name: "Japan", flag: "🇯🇵" },
];

export const DEVICE_TYPES = [
    { value: "mobile", label: "Mobile" },
    { value: "desktop", label: "Desktop" },
    { value: "tablet", label: "Tablet" },
] as const;

export const OPERATING_SYSTEMS = [
    "iOS",
    "Android",
    "Windows",
    "macOS",
    "Linux",
] as const;

export const BROWSERS = [
    "Chrome",
    "Firefox",
    "Safari",
    "Edge",
    "Opera",
] as const;

export type DeviceType = (typeof DEVICE_TYPES)[number]["value"];
export type OperatingSystem = (typeof OPERATING_SYSTEMS)[number];
export type Browser = (typeof BROWSERS)[number];
