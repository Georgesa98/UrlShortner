import { useSyncExternalStore } from "react";

function subscribe() {
    return () => {};
}
export default function useHostname() {
    const hostname = useSyncExternalStore(
        subscribe,
        () => window.location.hostname,
        () => ""
    );
    return hostname;
}
