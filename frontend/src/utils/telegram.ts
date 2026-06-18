declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        initData: string;
        platform: string;
      };
    };
  }
}

export function isTMA(): boolean {
  return Boolean(
    typeof window !== "undefined" &&
      window.Telegram?.WebApp?.initData
  );
}
