import { defineConfig } from "@neon/config/v1";

// askdocs infrastructure.
// Lakebase Postgres (always on) stores documents + chunks + query logs.
// Object Storage holds the original uploaded PDFs; chunks live in Postgres.
export default defineConfig({
  buckets: {
    uploads: {}, // private by default — PDFs are presigned on download
  },
});
