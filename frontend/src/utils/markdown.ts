// AI-generated interpretations are displayed as plain text (no markdown
// renderer), but the model occasionally emits markdown syntax anyway.
// Strips the common cases so raw **/*/#/- characters never leak into the UI.
export function stripMarkdown(text: string): string {
  return text
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/\*(.*?)\*/g, "$1")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/^[-*+]\s+/gm, "")
    .replace(/`([^`]*)`/g, "$1");
}
