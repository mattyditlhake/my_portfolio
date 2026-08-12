const { Pool } = require("pg");

/*
 * Reuse one database pool across Vercel function invocations where possible.
 * This reduces connection churn and keeps the visitor counter API lightweight.
 */
const pool = process.env.DATABASE_URL
  ? new Pool({
      connectionString: process.env.DATABASE_URL,
      ssl: { rejectUnauthorized: false },
    })
  : null;

/*
 * Ensure the visitor counter table exists before we read or update it.
 * The table stores a single logical counter row keyed by page name so the
 * portfolio can keep using one stable API route and one stable counter target.
 */
async function ensureVisitorTable() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS portfolio_visitors (
      page_name TEXT PRIMARY KEY,
      visit_count BIGINT NOT NULL DEFAULT 0,
      updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
  `);
}

/*
 * Read the current count without changing it.
 * This is used after a visitor has already been counted in the browser's
 * recent-visit window.
 */
async function getVisitorCount() {
  const result = await pool.query(
    `
      SELECT visit_count
      FROM portfolio_visitors
      WHERE page_name = $1
    `,
    ["home-profile"]
  );

  return Number(result.rows[0]?.visit_count || 0);
}

/*
 * Increment the count and return the updated value in one database round trip.
 * Using INSERT ... ON CONFLICT keeps concurrent visits safe and avoids race
 * conditions where two visitors arrive at the same time.
 */
async function incrementVisitorCount() {
  const result = await pool.query(
    `
      INSERT INTO portfolio_visitors (page_name, visit_count, updated_at)
      VALUES ($1, 1, NOW())
      ON CONFLICT (page_name)
      DO UPDATE
      SET visit_count = portfolio_visitors.visit_count + 1,
          updated_at = NOW()
      RETURNING visit_count
    `,
    ["home-profile"]
  );

  return Number(result.rows[0].visit_count);
}

module.exports = async function handler(req, res) {
  /*
   * This API route is intentionally limited to GET and POST:
   * - GET returns the current total
   * - POST increments the counter and returns the new total
   */
  if (req.method !== "GET" && req.method !== "POST") {
    res.status(405).json({ message: "Method not allowed." });
    return;
  }

  if (!pool) {
    res.status(503).json({
      message: "DATABASE_URL is not configured for the visitor counter.",
    });
    return;
  }

  try {
    await ensureVisitorTable();

    const count = req.method === "POST"
      ? await incrementVisitorCount()
      : await getVisitorCount();

    res.status(200).json({ count });
  } catch (error) {
    console.error("Visitor counter API error:", error);
    res.status(500).json({
      message: "Unable to process visitor counter right now.",
    });
  }
};
