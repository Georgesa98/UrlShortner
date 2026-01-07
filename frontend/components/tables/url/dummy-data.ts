import { Url } from "./columns";

export const urlDummyData: Url[] = [
    {
        id: "1",
        name: "Summer Sale 2024",
        short_url: "shrt.co/summer24",
        long_url:
            "https://yourstore.com/collections/summer-sale?utm_source=twitter...",
        url_status: {
            state: "ACTIVE",
        },
        created_at: "Oct 24, 2023",
        clicks: 1203,
    },
    {
        id: "2",
        name: "Personal Portfolio",
        short_url: "shrt.co/jdoe",
        long_url: "https://johndoe-design-portfolio.webflow.io/",
        url_status: {
            state: "ACTIVE",
        },
        created_at: "Oct 20, 2023",
        clicks: 845,
    },
    {
        id: "3",
        name: "Q3 Financial Report",
        short_url: "shrt.co/q3rep",
        long_url: "https://drive.google.com/file/d/123456789/view?usp=sharing",
        url_status: {
            state: "EXPIRED",
        }, // Example of a different status
        created_at: "Sep 15, 2023",
        clicks: 122,
    },
];
export const myUrlsDummyData: Url[] = [
    {
        id: "1",
        name: "Summer Sale 2024",
        short_url: "shrt.co/summer24",
        long_url:
            "https://yourstore.com/collections/summer-sale?utm_source=twitter...",
        status: "ACTIVE",
        created_at: "Oct 24, 2023",
        clicks: 1203,
    },
    {
        id: "2",
        name: "Personal Portfolio",
        short_url: "shrt.co/jdoe",
        long_url: "https://johndoe-design-portfolio.webflow.io/",
        status: "ACTIVE",
        created_at: "Oct 20, 2023",
        clicks: 845,
    },
    {
        id: "3",
        name: "Q3 Financial Report",
        short_url: "shrt.co/q3rep",
        long_url: "https://drive.google.com/file/d/123456789/view?usp=sharing",
        status: "EXPIRED", // Example of a different status
        created_at: "Sep 15, 2023",
        clicks: 122,
    },
    {
        id: "4",
        name: "Q3 Financial Report",
        short_url: "shrt.co/q3rep",
        long_url: "https://drive.google.com/file/d/123456789/view?usp=sharing",
        status: "EXPIRED", // Example of a different status
        created_at: "Sep 15, 2023",
        clicks: 122,
    },
];
