import { RefObject, useState } from "react";
import html2canvas from "html2canvas";

async function captureToFile(el: HTMLElement): Promise<File> {
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

export function useShareCard(ref: RefObject<HTMLElement | null>) {
  const [isLoading, setIsLoading] = useState(false);

  async function share() {
    if (!ref.current) return;
    setIsLoading(true);
    try {
      const file = await captureToFile(ref.current);
      if (navigator.share && navigator.canShare?.({ files: [file] })) {
        await navigator.share({ files: [file], title: "Mystral" });
      } else {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(file);
        a.download = "mystral-reading.png";
        a.click();
        URL.revokeObjectURL(a.href);
      }
    } catch (e) {
      if ((e as Error).name !== "AbortError") console.error("Share failed:", e);
    } finally {
      setIsLoading(false);
    }
  }

  async function shareToTelegram(text: string) {
    if (!ref.current) return;
    setIsLoading(true);
    try {
      const file = await captureToFile(ref.current);
      if (navigator.share && navigator.canShare?.({ files: [file] })) {
        await navigator.share({ files: [file], title: "Mystral", text });
      } else {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(file);
        a.download = "mystral-reading.png";
        a.click();
        URL.revokeObjectURL(a.href);
      }
    } catch (e) {
      if ((e as Error).name !== "AbortError") console.error("Share failed:", e);
    } finally {
      setIsLoading(false);
    }
  }

  return { share, shareToTelegram, isLoading };
}
