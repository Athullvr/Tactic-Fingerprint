"use client";

export default function Error({ reset }: { error: Error; reset: () => void }) {
  return <main className="error"><h1>Unable to load the tactical map.</h1><p>Check that the analytics API is running and derived signatures have been built.</p><button onClick={reset}>Try again</button></main>;
}
