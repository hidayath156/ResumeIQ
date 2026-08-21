async function api(url, opts = {}) {
    const r = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            ...(opts.headers || {})
        },
        ...opts
    });

    let d = {};

    try {
        d = await r.json();
    } catch (e) {}

    if (!r.ok) {
        throw new Error(d.error || "Request failed");
    }

    return d;
}