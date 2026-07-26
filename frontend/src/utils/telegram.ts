declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        initData: string;
        initDataUnsafe?: { start_param?: string };
        platform: string;
        BackButton?: {
          isVisible: boolean;
          show(): void;
          hide(): void;
          onClick(cb: () => void): void;
          offClick(cb: () => void): void;
        };
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
