import { useEffect, useState } from "react";
import { StarRating } from "./StarRating";

interface ReviewItem {
  id: string; user_name: string; zodiac_sign: string | null;
  rating: number; text: string | null; created_at: string | null;
}
interface Stats { average_rating: number; total_published: number; distribution: Record<string, number>; }

export function ReviewsBlock() {
  const [reviews, setReviews] = useState<ReviewItem[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    fetch("/api/v1/reviews/stats").then(r => r.json()).then(setStats).catch(() => {});
    loadMore(0);
  }, []);

  function loadMore(off: number) {
    fetch(`/api/v1/reviews/public?limit=10&offset=${off}`).then(r => r.json()).then(d => {
      setReviews(prev => off === 0 ? d.reviews : [...prev, ...d.reviews]);
      setHasMore(d.reviews.length === 10);
      setOffset(off + 10);
    }).catch(() => {});
  }

  if (!stats || stats.total_published === 0) return null;

  return (
    <div style={{ marginTop: 24 }}>
      <div style={{ display: "flex", alignItems: "flex-start", gap: 20, marginBottom: 20, flexWrap: "wrap" }}>
        <div>
          <span className="font-cormorant" style={{ fontSize: 52, color: "#F0E9DA", lineHeight: 1 }}>{stats.average_rating}</span>
          <div style={{ marginTop: 4 }}><StarRating value={Math.round(stats.average_rating)} size={16} readonly /></div>
          <p style={{ fontSize: 13, color: "#A89E8B", marginTop: 4 }}>{stats.total_published} отзывов</p>
        </div>
        <div style={{ flex: 1, minWidth: 140, display: "flex", flexDirection: "column", gap: 4 }}>
          {[5, 4, 3, 2, 1].map(n => {
            const count = stats.distribution[String(n)] || 0;
            const pct = stats.total_published > 0 ? (count / stats.total_published) * 100 : 0;
            return (
              <div key={n} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <span style={{ fontSize: 12, color: "#A89E8B", width: 12, textAlign: "right" }}>{n}</span>
                <span style={{ fontSize: 10, color: "#C9A84C" }}>★</span>
                <div style={{ flex: 1, height: 6, borderRadius: 99, background: "rgba(255,255,255,.08)", overflow: "hidden" }}>
                  <div style={{ width: `${pct}%`, height: "100%", borderRadius: 99, background: "linear-gradient(90deg,#8A6E2E,#E8CD7E)" }} />
                </div>
                <span style={{ fontSize: 12, color: "#827A69", width: 24 }}>{count}</span>
              </div>
            );
          })}
        </div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {reviews.map(r => (
          <div key={r.id} style={{ padding: "18px 20px", borderRadius: 16, background: "linear-gradient(155deg,rgba(255,255,255,.04),rgba(255,255,255,.01))", border: "1px solid rgba(255,255,255,.07)" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <div style={{ width: 36, height: 36, borderRadius: "50%", background: "linear-gradient(135deg,#4B3C86,#C9A84C)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <span className="font-cormorant" style={{ fontSize: 16, color: "#0C0A18" }}>{(r.user_name || "?")[0]?.toUpperCase()}</span>
                </div>
                <div>
                  <p style={{ fontSize: 14, color: "#F0E9DA", fontWeight: 500 }}>{r.user_name}</p>
                  {r.zodiac_sign && <p style={{ fontSize: 12, color: "#C9A84C" }}>{r.zodiac_sign}</p>}
                </div>
              </div>
              <StarRating value={r.rating} size={14} readonly />
            </div>
            {r.text && <p style={{ fontSize: 14, lineHeight: 1.7, color: "#B6AC98", marginTop: 10 }}>{r.text}</p>}
            {r.created_at && (
              <p style={{ fontSize: 11, color: "#827A69", marginTop: 8 }}>
                {new Date(r.created_at).toLocaleDateString("ru-RU", { day: "numeric", month: "long", year: "numeric" })}
              </p>
            )}
          </div>
        ))}
      </div>

      {hasMore && reviews.length > 0 && (
        <button onClick={() => loadMore(offset)} style={{ width: "100%", height: 42, marginTop: 12, borderRadius: 12, border: "1px solid rgba(201,168,76,.4)", background: "rgba(201,168,76,.06)", color: "#E8CD7E", fontSize: 13, cursor: "pointer" }}>
          Показать ещё
        </button>
      )}
    </div>
  );
}
