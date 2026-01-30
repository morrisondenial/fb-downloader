
const { getFbVideoInfo } = require("fb-downloader-scrapper");

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: "Only POST allowed" });
    }

    const { url } = req.body;
    if (!url) {
        return res.status(400).json({ error: "No URL provided" });
    }

    try {
        const result = await getFbVideoInfo(url);
        res.status(200).json({ ok: true, links: result });
    } catch (error) {
        res.status(500).json({ ok: false, error: "Video not found or link is private" });
    }
}
