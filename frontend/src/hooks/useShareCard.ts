import { RefObject, useState } from "react";
import { useTranslation } from "react-i18next";

async function captureToFile(el: HTMLElement): Promise<File> {
  // Dynamic import keeps html2canvas (~200KB) out of the main bundle —
  // it loads only when the user actually opens a share card.
  const html2canvas = (await import("html2canvas")).default;
  await document.fonts.ready;
  const canvas = await html2canvas(el, {
    scale: 2,
    useCORS: true,
    backgroundColor: "#07060F",
    logging: false,
  });
  const blob = await new Promise<Blob>((resolve) =>
    canvas.toBlob((b) => resolve(b!), "image/png")
  );
  return new File([blob], "mystral-reading.png", { type: "image/png" });
}

function downloadFile(file: File) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(file);
  a.download = file.name;
  a.click();
  URL.revokeObjectURL(a.href);
}

export function useShareCard(ref: RefObject<HTMLElement | null>) {
  const { t } = useTranslation();
  const [isLoading, setIsLoading] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  // Always a plain, predictable download — no OS share sheet detour. Inside
  // Telegram's in-app browser navigator.share for files is unreliable, so a
  // button literally labeled "download" should just download.
  async function share() {
    if (!ref.current) return;
    setIsLoading(true);
    setFeedback(null);
    try {
      const file = await captureToFile(ref.current);
      downloadFile(file);
    } catch (e) {
      console.error("Download failed:", e);
    } finally {
      setIsLoading(false);
    }
  }

  async function shareToTelegram(text: string) {
    if (!ref.current) return;
    setIsLoading(true);
    setFeedback(null);
    try {
      const file = await captureToFile(ref.current);

      // Writing the image to the clipboard ourselves (with an explicit
      // image/png ClipboardItem) is more reliable for "paste into a Telegram
      // chat" than navigator.share's file handoff, which inside Telegram's
      // own in-app browser can report success ("copied") while handing the
      // target app something that doesn't actually paste as an image.
      if (navigator.clipboard && typeof ClipboardItem !== "undefined") {
        try {
          await navigator.clipboard.write([new ClipboardItem({ "image/png": file })]);
          setFeedback(t("share.copied_hint"));
          return;
        } catch {
          // Clipboard image write unsupported or denied — fall through.
        }
      }

      if (navigator.share && navigator.canShare?.({ files: [file] })) {
        await navigator.share({ files: [file], title: "Mystral", text });
        return;
      }

      downloadFile(file);
      setFeedback(t("share.download_hint"));
    } catch (e) {
      if ((e as Error).name !== "AbortError") console.error("Share failed:", e);
    } finally {
      setIsLoading(false);
    }
  }

  return { share, shareToTelegram, isLoading, feedback };
}
