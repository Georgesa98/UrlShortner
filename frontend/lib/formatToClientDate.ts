export const formatToClientDate = (isoString: string): string => {
    if (!isoString) return "";

    const date = new Date(isoString);

    if (isNaN(date.getTime())) {
        console.error("Invalid date provided to formatToClientDate");
        return "";
    }

    return new Intl.DateTimeFormat("en-GB", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
    })
        .format(date)
        .replace(/\//g, "-");
};
